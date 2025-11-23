"""
Agent Mode - Autonomous AI Agent with Screen Analysis
Integrates with Ollama for flexible model selection
Includes screen capture, task automation, and permission system
"""

import json
import time
import logging
import asyncio
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import base64
import io
import re

from ui_detection_improved import DetectionResult, StartButtonDetector

# Import task templates
try:
    from agent_templates import enhance_task_prompt, get_task_hints
except ImportError:
    # Fallback if templates not available
    def enhance_task_prompt(task: str) -> str:
        return task
    def get_task_hints(task: str) -> dict:
        return {"detected_intent": None, "suggested_actions": [], "shortcuts": []}

try:
    import requests
except ImportError:
    import subprocess
    import sys
    subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
    import requests

try:
    from PIL import ImageGrab, Image
except ImportError:
    import subprocess
    import sys
    subprocess.run([sys.executable, "-m", "pip", "install", "pillow"], check=True)
    from PIL import ImageGrab, Image

try:
    import pyautogui
except ImportError:
    import subprocess
    import sys
    subprocess.run([sys.executable, "-m", "pip", "install", "pyautogui"], check=True)
    import pyautogui

# Disable PyAutoGUI fail-safe for controlled automation
pyautogui.FAILSAFE = False

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available_models = []
        
    def check_connection(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            # Ollama is not running
            return False
        except Exception as e:
            logging.warning(f"Ollama connection check failed: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model['name'] for model in data.get('models', [])]
                return self.available_models
            return []
        except Exception as e:
            logging.error(f"Failed to list models: {e}")
            return []
    
    def generate(self, model: str, prompt: str, images: List[str] = None, stream: bool = False, keep_alive: str = "5m", timeout: int = 30) -> Dict:
        """Generate response from Ollama model with memory control and cancellation support"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream,
                "keep_alive": keep_alive,  # Control how long model stays in VRAM
                "options": {
                    "num_ctx": 4096,  # Reduced context window for better performance
                    "num_gpu": 99,  # Force ALL layers to GPU (99 = use all available GPU layers)
                    "num_thread": 2,  # Reduce CPU threads to prioritize GPU
                    "numa": False  # Disable NUMA for single GPU systems
                }
            }
            
            if images:
                payload["images"] = images
            
            # Use shorter timeout for faster cancellation
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout  # Configurable timeout, default 30s
            )
            
            if response.status_code == 200:
                if stream:
                    return {"success": True, "response": response}
                else:
                    return {"success": True, "response": response.json().get('response', '')}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logging.error(f"Generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def chat(self, model: str, messages: List[Dict], images: List[str] = None, keep_alive: str = "5m", timeout: int = 30) -> Dict:
        """Chat with Ollama model with memory control and cancellation support"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "keep_alive": keep_alive,  # Control memory usage
                "options": {
                    "num_ctx": 4096,
                    "num_gpu": 99,  # Force ALL layers to GPU (99 = use all available GPU layers)
                    "num_thread": 2,  # Reduce CPU threads to prioritize GPU
                    "numa": False  # Disable NUMA for single GPU systems
                }
            }
            
            if images:
                payload["images"] = images
            
            # Use shorter timeout for faster cancellation
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=timeout  # Configurable timeout, default 30s
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message": data.get('message', {}),
                    "response": data.get('message', {}).get('content', '')
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logging.error(f"Chat failed: {e}")
            return {"success": False, "error": str(e)}
    
    def unload_model(self, model: str) -> Dict:
        """Unload a model from VRAM/memory immediately"""
        try:
            logging.info(f"Unloading model: {model}")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "keep_alive": 0  # Unload immediately
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logging.info(f"✓ Model {model} unloaded from memory")
                return {"success": True}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            logging.error(f"Model unload failed: {e}")
            return {"success": False, "error": str(e)}


class ScreenAnalyzer:
    """Handles screen capture and analysis"""
    
    def __init__(self, screenshots_dir: Path, max_dimension: int = 1080):
        self.screenshots_dir = screenshots_dir
        self.screenshots_dir.mkdir(exist_ok=True)
        self.last_screenshot = None
        self.max_dimension = max_dimension  # Maximum width or height for optimization
        
    def capture_screen(self, region=None) -> Optional[str]:
        """Capture screen and return base64 encoded image (optimized for vision models)"""
        try:
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            
            # Get original dimensions
            original_width, original_height = screenshot.size
            logging.info(f"Screenshot captured: {original_width}x{original_height} (full resolution, no resizing)")
            
            # Save optimized screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.screenshots_dir / f"screen_{timestamp}.jpg"
            
            # Save as JPEG with quality 85 for better compression
            screenshot.save(filepath, format='JPEG', quality=85, optimize=True)
            self.last_screenshot = filepath
            
            # Convert to base64 (use JPEG for smaller payload)
            buffer = io.BytesIO()
            screenshot.save(buffer, format='JPEG', quality=85, optimize=True)
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Clean up buffer
            buffer.close()
            del buffer
            
            logging.info(f"Screenshot size: {len(img_base64)} bytes")
            
            return img_base64
            
        except Exception as e:
            logging.error(f"Screen capture failed: {e}")
            return None
        finally:
            # Force garbage collection
            import gc
            gc.collect()
    
    def get_screen_dimensions(self) -> Tuple[int, int]:
        """Get current screen dimensions"""
        try:
            width, height = pyautogui.size()
            return (width, height)
        except Exception:
            return (2560, 1440)  # Default fallback
    
    def cleanup_old_screenshots(self, keep_last: int = 10):
        """Delete old screenshots to prevent disk space buildup"""
        try:
            screenshots = sorted(self.screenshots_dir.glob("screen_*.jpg"), key=lambda x: x.stat().st_mtime, reverse=True)
            screenshots += sorted(self.screenshots_dir.glob("screen_*.png"), key=lambda x: x.stat().st_mtime, reverse=True)
            
            if len(screenshots) > keep_last:
                for old_file in screenshots[keep_last:]:
                    try:
                        old_file.unlink()
                        logging.debug(f"Deleted old screenshot: {old_file.name}")
                    except Exception as e:
                        logging.warning(f"Could not delete {old_file}: {e}")
        except Exception as e:
            logging.error(f"Screenshot cleanup failed: {e}")
    
    def get_screen_info(self) -> Dict:
        """Get screen resolution and info"""
        try:
            width, height = pyautogui.size()
            return {
                "width": width,
                "height": height,
                "position": pyautogui.position()
            }
        except Exception as e:
            logging.error(f"Failed to get screen info: {e}")
            return {}


class UIElementDetector:
    """Detects UI elements using pure OpenCV - no vision models"""
    
    def __init__(self, ollama_client: OllamaClient, screen_analyzer: ScreenAnalyzer):
        from pathlib import Path
        from ui_detection_improved import GenericUIDetector
        
        self.ollama = ollama_client  # Not used, kept for compatibility
        self.screen_analyzer = screen_analyzer
        self.detected_elements = {}  # Cache of detected elements
        
        # Initialize all UI detectors
        self.start_detector: Optional[StartButtonDetector] = None
        self.edge_detector: Optional[GenericUIDetector] = None
        self.folders_detector: Optional[GenericUIDetector] = None
        self.searchbar_detector: Optional[GenericUIDetector] = None
        
        symbols_dir = Path(__file__).parent / "Symbols"

        try:
            # Start button detector (with fallback to synthetic template)
            self.start_detector = StartButtonDetector()
            logging.info("✓ Start button detector initialized")
        except Exception as e:
            logging.warning(f"Start detector unavailable: {e}")
        
        try:
            # Edge browser detector
            edge_path = symbols_dir / "EdgeBrowser.png"
            if edge_path.exists():
                self.edge_detector = GenericUIDetector(str(edge_path), "Edge Browser", roi_region="taskbar")
                logging.info("✓ Edge browser detector initialized")
        except Exception as e:
            logging.warning(f"Edge detector unavailable: {e}")
        
        try:
            # Folders/File Explorer detector
            folders_path = symbols_dir / "Folders.png"
            if folders_path.exists():
                self.folders_detector = GenericUIDetector(str(folders_path), "File Explorer", roi_region="taskbar")
                logging.info("✓ File Explorer detector initialized")
        except Exception as e:
            logging.warning(f"Folders detector unavailable: {e}")
        
        try:
            # Search bar detector (taskbar search)
            searchbar_path = symbols_dir / "SearchTaskBar.png"
            if searchbar_path.exists():
                self.searchbar_detector = GenericUIDetector(str(searchbar_path), "Search Bar", roi_region="taskbar")
                logging.info("✓ Search bar detector initialized")
        except Exception as e:
            logging.warning(f"Search bar detector unavailable: {e}")
        
        logging.info("✓ OpenCV-based UI detection initialized (no vision models)")
        
    def detect_elements(self, screenshot_b64: str, element_query: str = None) -> List[Dict]:
        """
        Detect UI elements using pure OpenCV (no vision models)
        Returns list of elements with their exact coordinates
        
        Args:
            screenshot_b64: Base64 encoded screenshot
            element_query: Optional - specific element to find (e.g., "Start button", "Edge browser", "File Explorer")
        
        Returns:
            List of dicts: [{"name": "Start button", "x": 50, "y": 1400, "width": 40, "height": 40}, ...]
        """
        try:
            if not element_query:
                logging.warning("No element query provided for detection")
                return []
            
            query_lower = element_query.lower()
            
            # Try Start button detector
            if any(kw in query_lower for kw in ("start button", "start menu", "windows start")):
                if self.start_detector:
                    detection = self.start_detector.detect_from_base64(screenshot_b64)
                    if detection:
                        element = {
                            "name": detection.name,
                            "x": detection.x,
                            "y": detection.y,
                            "width": detection.width,
                            "height": detection.height,
                            "confidence": round(detection.confidence, 3),
                            "description": "Detected via OpenCV",
                            "method": detection.method,
                        }
                        logging.info("✓ Found %s at (%d, %d) [conf: %.2f]", 
                                   element["name"], element["x"], element["y"], element["confidence"])
                        self.detected_elements[element["name"]] = element
                        return [element]
                    logging.warning("Start detector did not find element")
                    return []
            
            # Try Edge browser detector
            if any(kw in query_lower for kw in ("edge", "browser", "microsoft edge")):
                if self.edge_detector:
                    detection = self.edge_detector.detect_from_base64(screenshot_b64)
                    if detection:
                        element = {
                            "name": detection.name,
                            "x": detection.x,
                            "y": detection.y,
                            "width": detection.width,
                            "height": detection.height,
                            "confidence": round(detection.confidence, 3),
                            "description": "Detected via OpenCV",
                            "method": detection.method,
                        }
                        logging.info("✓ Found %s at (%d, %d) [conf: %.2f]", 
                                   element["name"], element["x"], element["y"], element["confidence"])
                        self.detected_elements[element["name"]] = element
                        return [element]
                    logging.warning("Edge detector did not find element")
                    return []
            
            # Try File Explorer detector
            if any(kw in query_lower for kw in ("file explorer", "folders", "folder", "explorer")):
                if self.folders_detector:
                    detection = self.folders_detector.detect_from_base64(screenshot_b64)
                    if detection:
                        element = {
                            "name": detection.name,
                            "x": detection.x,
                            "y": detection.y,
                            "width": detection.width,
                            "height": detection.height,
                            "confidence": round(detection.confidence, 3),
                            "description": "Detected via OpenCV",
                            "method": detection.method,
                        }
                        logging.info("✓ Found %s at (%d, %d) [conf: %.2f]", 
                                   element["name"], element["x"], element["y"], element["confidence"])
                        self.detected_elements[element["name"]] = element
                        return [element]
                    logging.warning("Folders detector did not find element")
                    return []
            
            # Try Search bar detector
            if any(kw in query_lower for kw in ("search", "search bar")):
                if self.searchbar_detector:
                    detection = self.searchbar_detector.detect_from_base64(screenshot_b64)
                    if detection:
                        element = {
                            "name": detection.name,
                            "x": detection.x,
                            "y": detection.y,
                            "width": detection.width,
                            "height": detection.height,
                            "confidence": round(detection.confidence, 3),
                            "description": "Detected via OpenCV",
                            "method": detection.method,
                        }
                        logging.info("✓ Found %s at (%d, %d) [conf: %.2f]", 
                                   element["name"], element["x"], element["y"], element["confidence"])
                        self.detected_elements[element["name"]] = element
                        return [element]
                    logging.warning("Search bar detector did not find element")
                    return []
            
            # No detector available for this element
            logging.warning(f"No detector available for '{element_query}'")
            return []
            
        except Exception as e:
            logging.error(f"UI element detection failed: {e}")
            return []
    
    def find_element(self, element_name: str, screenshot_b64: str = None) -> Optional[Dict]:
        """
        Find a specific UI element by name
        Returns element dict with coordinates or None if not found
        """
        # Check cache first
        if element_name in self.detected_elements:
            return self.detected_elements[element_name]
        
        # If screenshot provided, detect it
        if screenshot_b64:
            elements = self.detect_elements(screenshot_b64, element_query=element_name)
            if elements:
                return elements[0]
        
        return None
    
    def get_click_coordinates(self, element_name: str, screenshot_b64: str = None) -> Optional[Tuple[int, int]]:
        """
        Get exact click coordinates for a named element
        Returns (x, y) tuple or None if element not found
        """
        element = self.find_element(element_name, screenshot_b64)
        if element and 'x' in element and 'y' in element:
            return (element['x'], element['y'])
        return None


class TaskExecutor:
    """Executes tasks based on AI decisions with user permission"""
    
    def __init__(self):
        self.pending_actions = []
        self.action_history = []
        self.permissions = {
            "mouse_click": False,
            "keyboard_type": False,
            "file_operations": False,
            "system_commands": False
        }
    
    def request_permission(self, action_type: str) -> bool:
        """Check if permission is granted for action type"""
        return self.permissions.get(action_type, False)
    
    def set_permission(self, action_type: str, granted: bool):
        """Set permission for action type"""
        self.permissions[action_type] = granted
        logging.info(f"Permission {'granted' if granted else 'denied'} for: {action_type}")
    
    def execute_mouse_click(self, x: int, y: int, button: str = 'left') -> Dict:
        """Execute mouse click with permission check"""
        if not self.request_permission("mouse_click"):
            return {"success": False, "error": "Permission denied: mouse_click"}
        
        try:
            pyautogui.click(x, y, button=button)
            action = {
                "type": "mouse_click",
                "x": x, "y": y,
                "button": button,
                "timestamp": datetime.now().isoformat()
            }
            self.action_history.append(action)
            return {"success": True, "action": action}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_keyboard_type(self, text: str, interval: float = 0.05) -> Dict:
        """Type text with permission check"""
        if not self.request_permission("keyboard_type"):
            return {"success": False, "error": "Permission denied: keyboard_type"}
        
        try:
            pyautogui.write(text, interval=interval)
            action = {
                "type": "keyboard_type",
                "text": text[:50],  # Log first 50 chars
                "timestamp": datetime.now().isoformat()
            }
            self.action_history.append(action)
            return {"success": True, "action": action}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_key_press(self, key: str) -> Dict:
        """Press a specific key"""
        if not self.request_permission("keyboard_type"):
            return {"success": False, "error": "Permission denied: keyboard_type"}
        
        try:
            pyautogui.press(key)
            action = {
                "type": "key_press",
                "key": key,
                "timestamp": datetime.now().isoformat()
            }
            self.action_history.append(action)
            return {"success": True, "action": action}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_hotkey(self, *keys) -> Dict:
        """Press a combination of keys (e.g., Ctrl+T)"""
        if not self.request_permission("keyboard_type"):
            return {"success": False, "error": "Permission denied: keyboard_type"}
        
        try:
            pyautogui.hotkey(*keys)
            action = {
                "type": "hotkey",
                "keys": "+".join(keys),
                "timestamp": datetime.now().isoformat()
            }
            self.action_history.append(action)
            return {"success": True, "action": action}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def open_application(self, app_name: str) -> Dict:
        """Open an application or program"""
        if not self.request_permission("system_commands"):
            return {"success": False, "error": "Permission denied: system_commands"}
        
        try:
            # Map common app names to Windows commands
            app_commands = {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "explorer": "explorer.exe",
                "cmd": "cmd.exe",
                "powershell": "powershell.exe",
                "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                "edge": "msedge.exe",
                "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe"
            }
            
            command = app_commands.get(app_name.lower(), app_name)
            subprocess.Popen(command, shell=True)
            
            action = {
                "type": "open_application",
                "app": app_name,
                "timestamp": datetime.now().isoformat()
            }
            self.action_history.append(action)
            return {"success": True, "action": action}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_mouse_move(self, x: int, y: int, duration: float = 0.5) -> Dict:
        """Move mouse to position"""
        if not self.request_permission("mouse_click"):
            return {"success": False, "error": "Permission denied: mouse_click"}
        
        try:
            pyautogui.moveTo(x, y, duration=duration)
            action = {
                "type": "mouse_move",
                "x": x, "y": y,
                "timestamp": datetime.now().isoformat()
            }
            self.action_history.append(action)
            return {"success": True, "action": action}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_action_history(self, limit: int = 50) -> List[Dict]:
        """Get recent action history"""
        return self.action_history[-limit:]
    
    def execute_escape(self) -> Dict:
        """Press Escape key - useful for dismissing dialogs"""
        if not self.request_permission("keyboard_type"):
            return {"success": False, "error": "Permission denied: keyboard_type"}
        
        try:
            pyautogui.press('esc')
            action = {
                "type": "escape",
                "timestamp": datetime.now().isoformat()
            }
            self.action_history.append(action)
            return {"success": True, "action": action}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_alt_tab(self) -> Dict:
        """Switch to next window"""
        if not self.request_permission("keyboard_type"):
            return {"success": False, "error": "Permission denied: keyboard_type"}
        
        try:
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.3)
            action = {
                "type": "alt_tab",
                "timestamp": datetime.now().isoformat()
            }
            self.action_history.append(action)
            return {"success": True, "action": action}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_ctrl_n(self) -> Dict:
        """Open new window/tab (Ctrl+N) - useful for handling unsaved work prompts"""
        if not self.request_permission("keyboard_type"):
            return {"success": False, "error": "Permission denied: keyboard_type"}
        
        try:
            pyautogui.hotkey('ctrl', 'n')
            time.sleep(0.5)
            action = {
                "type": "ctrl_n",
                "description": "New window/document",
                "timestamp": datetime.now().isoformat()
            }
            self.action_history.append(action)
            return {"success": True, "action": action}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_select_all(self) -> Dict:
        """Select all text (Ctrl+A)"""
        if not self.request_permission("keyboard_type"):
            return {"success": False, "error": "Permission denied: keyboard_type"}
        
        try:
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            action = {
                "type": "select_all",
                "timestamp": datetime.now().isoformat()
            }
            self.action_history.append(action)
            return {"success": True, "action": action}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_save_file(self) -> Dict:
        """Save file (Ctrl+S)"""
        if not self.request_permission("file_operations"):
            return {"success": False, "error": "Permission denied: file_operations"}
        
        try:
            pyautogui.hotkey('ctrl', 's')
            time.sleep(0.3)
            action = {
                "type": "save_file",
                "timestamp": datetime.now().isoformat()
            }
            self.action_history.append(action)
            return {"success": True, "action": action}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_double_click(self, x: int, y: int) -> Dict:
        """Double-click at position"""
        if not self.request_permission("mouse_click"):
            return {"success": False, "error": "Permission denied: mouse_click"}
        
        try:
            pyautogui.doubleClick(x, y)
            action = {
                "type": "double_click",
                "x": x, "y": y,
                "timestamp": datetime.now().isoformat()
            }
            self.action_history.append(action)
            return {"success": True, "action": action}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_right_click(self, x: int, y: int) -> Dict:
        """Right-click at position"""
        if not self.request_permission("mouse_click"):
            return {"success": False, "error": "Permission denied: mouse_click"}
        
        try:
            pyautogui.rightClick(x, y)
            action = {
                "type": "right_click",
                "x": x, "y": y,
                "timestamp": datetime.now().isoformat()
            }
            self.action_history.append(action)
            return {"success": True, "action": action}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_scroll(self, amount: int) -> Dict:
        """Scroll up (positive) or down (negative)"""
        if not self.request_permission("mouse_click"):
            return {"success": False, "error": "Permission denied: mouse_click"}
        
        try:
            pyautogui.scroll(amount)
            action = {
                "type": "scroll",
                "amount": amount,
                "timestamp": datetime.now().isoformat()
            }
            self.action_history.append(action)
            return {"success": True, "action": action}
        except Exception as e:
            return {"success": False, "error": str(e)}


class AgentMode:
    """Main autonomous agent with Ollama integration"""
    
    def __init__(self, base_dir: Path, ollama_url: str = "http://localhost:11434"):
        self.base_dir = base_dir
        self.screenshots_dir = base_dir / "agent_screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        self.cancel_requested = False  # Emergency stop flag
        
        self.ollama = OllamaClient(ollama_url)
        self.screen_analyzer = ScreenAnalyzer(self.screenshots_dir)
        self.task_executor = TaskExecutor()
        self.ui_detector = UIElementDetector(self.ollama, self.screen_analyzer)
        
        self.current_model = None
        self.conversation_history = []
        self.active = False
        self.task_queue = []
        self.last_detected_coords = None  # Store last detected UI element coordinates
        
        # Initialize overlay
        self.overlay = None
        try:
            from agent_overlay import get_overlay
            self.overlay = get_overlay()
        except Exception as e:
            logging.warning(f"Could not initialize overlay: {e}")
        
    def cancel_operation(self) -> Dict:
        """Emergency stop - INSTANT cancel current operation and unload model"""
        logging.info("[Agent] EMERGENCY STOP requested - FORCING IMMEDIATE CANCELLATION")
        self.cancel_requested = True
        
        # Stop overlay immediately
        if self.overlay:
            try:
                self.overlay.update_reasoning("❌ EMERGENCY STOP - Cancelling...")
                self.overlay.stop()
            except:
                pass
        
        # Kill any ongoing Ollama requests by unloading ALL models
        try:
            # Get list of loaded models
            response = requests.get(f"{self.ollama.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                for model_info in models:
                    model_name = model_info.get('name', '')
                    if model_name:
                        logging.info(f"[Emergency] Unloading: {model_name}")
                        self.ollama.unload_model(model_name)
        except Exception as e:
            logging.warning(f"Could not unload all models: {e}")
        
        # Unload current model
        if self.current_model:
            logging.info(f"[Agent] Force unloading model: {self.current_model}")
            self.ollama.unload_model(self.current_model)
        
        # Force garbage collection
        import gc
        gc.collect()
        
        logging.info("[Agent] EMERGENCY STOP complete")
        return {
            "success": True,
            "message": "⚠️ EMERGENCY STOP - All operations cancelled and models unloaded"
        }
    
    def check_ollama_status(self) -> Dict:
        """Check if Ollama is available and get models"""
        connected = self.ollama.check_connection()
        models = self.ollama.list_models() if connected else []
        
        return {
            "connected": connected,
            "models": models,
            "current_model": self.current_model
        }
    
    def set_model(self, model: str) -> Dict:
        """Set the active Ollama model"""
        try:
            models = self.ollama.list_models()
            if model in models:
                self.current_model = model
                return {"success": True, "model": model}
            else:
                return {"success": False, "error": f"Model '{model}' not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_screen(self, prompt: str = "Describe what you see on the screen.") -> Dict:
        """Capture screen and analyze with vision model"""
        if not self.current_model:
            return {"success": False, "error": "No model selected"}
        
        # Capture screen
        screenshot_base64 = self.screen_analyzer.capture_screen()
        if not screenshot_base64:
            return {"success": False, "error": "Failed to capture screen"}
        
        # Analyze with Ollama (vision models like llava)
        result = self.ollama.generate(
            model=self.current_model,
            prompt=prompt,
            images=[screenshot_base64]
        )
        
        if result["success"]:
            analysis = {
                "success": True,
                "analysis": result["response"],
                "screenshot": self.screen_analyzer.last_screenshot.name,
                "timestamp": datetime.now().isoformat()
            }
            return analysis
        else:
            return result
    
    def execute_task(self, task: str, auto_execute: bool = True) -> Dict:
        """Execute a task with AI reasoning and automatic multi-step execution"""
        if not self.current_model:
            return {"success": False, "error": "No model selected"}
        
        # Grant all permissions for autonomous agent operation
        logging.info("[Agent] Auto-granting all permissions for autonomous operation")
        self.task_executor.set_permission("mouse_click", True)
        self.task_executor.set_permission("keyboard_type", True)
        self.task_executor.set_permission("file_operations", True)
        self.task_executor.set_permission("system_commands", True)
        
        # Start overlay FIRST if available with initial message
        if self.overlay:
            self.overlay.start()
            time.sleep(1.5)  # Give overlay time to fully initialize
            self.overlay.update_reasoning(f"🚀 Starting task: {task[:100]}...")
        
        # Enhance task with template if available
        enhanced_task = enhance_task_prompt(task)
        task_hints = get_task_hints(task)
        
        logging.info(f"[Agent] Starting task: {task}")
        if task_hints.get("detected_intent"):
            logging.info(f"[Agent] Detected intent: {task_hints['detected_intent']}")
        
        execution_log = []
        execution_log.append(f"Original task: {task}")
        if task_hints.get("suggested_actions"):
            execution_log.append(f"Detected intent: {task_hints['detected_intent']}")
        
        steps_completed = 0
        max_steps = 15  # Increased for complex tasks like YouTube browsing
        last_action = None  # Track last action to detect loops
        repeat_count = 0  # Count how many times same action repeats
        
        # Initialize conversation context for this task
        task_context = []  # Store previous steps to maintain context
        
        try:
            # Reset cancel flag at start
            self.cancel_requested = False
            
            for step in range(max_steps):
                # Check for cancellation
                if self.cancel_requested:
                    logging.info("[Agent] Task cancelled by user")
                    execution_log.append("❌ Task cancelled by user")
                    return {
                        "success": False,
                        "error": "Operation cancelled by user",
                        "execution_log": execution_log,
                        "steps_completed": steps_completed
                    }
                
                # IMPORTANT: Capture screenshot BEFORE showing overlay
                # This prevents AI from seeing its own reasoning text
                screenshot_base64 = self.screen_analyzer.capture_screen()
                
                # Screenshot captured - overlay is always visible (click-through enabled)
                
                if not screenshot_base64:
                    return {"success": False, "error": "Failed to capture screen"}
                
                # Get screen dimensions for AI awareness
                screen_info = self.screen_analyzer.get_screen_info()
                screen_size = f"{screen_info.get('width', 0)}x{screen_info.get('height', 0)}"
                
                # Build context from previous steps
                context_summary = ""
                if task_context:
                    context_summary = "\n\nPREVIOUS STEPS (what you've already done):\n"
                    for i, ctx in enumerate(task_context[-5:], 1):  # Show last 5 steps only
                        context_summary += f"{i}. {ctx['action']}: {ctx['reasoning']}\n"
                        if ctx.get('result'):
                            context_summary += f"   Result: {ctx['result']}\n"
                    context_summary += "\nRemember what you already did! Don't repeat successful actions.\n"
                
                # Ask AI what to do next - with thinking allowed but JSON required
                prompt = f"""TASK: {enhanced_task}
Step {step + 1}/{max_steps} | Screen Resolution: {screen_size}
{context_summary}
ANALYZE THE FULL RESOLUTION SCREENSHOT:
Look carefully at what's on screen. Describe what you see, then decide the next action.

You can THINK OUT LOUD, but your final response MUST end with valid JSON in this format:

THINKING: [Describe what you see and your reasoning]

```json
{{
    "observation": "what I see on screen",
    "action": "action_name",
    "reasoning": "why this action",
    "parameters": {{}},
    "task_complete": false
}}
```

AVAILABLE ACTIONS (prefer mouse-based interaction):

**PRIMARY ACTIONS** (use these for navigation):
- detect_ui_element: {{"element_name": "Start button"}} - **PREFERRED**: Auto-detect UI element and get EXACT coordinates
- mouse_move: {{"x": 100, "y": 200}} - Move mouse to specific coordinates (use before clicking)
- mouse_click: {{"x": 100, "y": 200, "button": "left"}} - Click at coordinates (left/right/middle)
- double_click: {{"x": 100, "y": 200}} - Double-click at coordinates (opens files/folders)
- right_click: {{"x": 100, "y": 200}} - Right-click for context menus

**INTERACTION ACTIONS**:
- keyboard_type: {{"text": "your text here"}} - Type text in focused window
- key_press: {{"key": "enter"}} - Press single key (enter, tab, escape, space, etc.)
- hotkey: {{"keys": ["ctrl", "c"]}} - Press key combinations (ctrl+c, alt+tab, win+r, etc.)
- scroll: {{"amount": 3}} - Scroll mouse wheel (positive=down, negative=up)

**UTILITY ACTIONS**:
- wait: {{"seconds": 2}} - Wait for UI to respond/load
- complete: {{}} - Mark task as finished

**DISCOURAGED** (only use if mouse navigation impossible):
- open_app: {{"app": "appname"}} - Launch application via command line

**💡 TIP: Use detect_ui_element FIRST before manual coordinate guessing!**
Example: detect_ui_element with "Start button", "Calculator icon", "Close button", etc.
This gives you EXACT pixel coordinates automatically!

**CRITICAL: HOW TO FIND COORDINATES IN SCREENSHOTS**:

Screen dimensions: {screen_size} pixels
Coordinate system: (0, 0) = top-left corner, ({screen_size}) = bottom-right corner

**STEP-BY-STEP COORDINATE FINDING**:

1. **Identify the target element** in the screenshot image (button, icon, text field, etc.)

2. **Estimate its position using visual grid method**:
   - Imagine the screen divided into a 10x10 grid
   - Count grid squares from left edge to find element's horizontal position
   - Count grid squares from top edge to find element's vertical position
   
3. **Convert grid position to pixel coordinates**:
   - Example for screen size 2560x1440:
     * If element is 1/10 from left → x ≈ 256 pixels
     * If element is 5/10 from left → x ≈ 1280 pixels (middle)
     * If element is 9/10 from left → x ≈ 2304 pixels
     * If element is 9/10 from top → y ≈ 1296 pixels (near bottom)
   - ALWAYS target the CENTER of the element, not its edge

4. **Common UI element positions to help calibrate**:
   - Windows Start button: Very bottom-left corner (x≈20-60, y≈screen_height-30)
   - Taskbar icons: Bottom row (y≈screen_height-30 to screen_height-50)
   - Window close button (X): Top-right of window title bar
   - Maximize/minimize: Just left of close button
   
5. **Adaptive clicking strategy**:
   - Make your best coordinate estimate from visual analysis
   - If you miss, use mouse_move to relocate and try again
   - Adjust by ±50-100 pixels in the direction you need to move
- **Window title bars**: Top of each window (look for minimize/maximize/close buttons)
- **Start button**: Bottom-left area (examine screenshot to find exact Windows logo position)
- **System tray**: Bottom-right area (look for clock, notification icons)

**DO NOT use hardcoded coordinates! ALWAYS estimate from visual analysis!**

UNIVERSAL WINDOW DETECTION GUIDE:
Examine the ENTIRE screen systematically. Look for these universal window features:

**Title Bar Identification** (top edge of windows):
- Look for rectangular bars at the TOP of any window
- Title bars contain: app name, document name, or "Untitled"
- Right side has: minimize (-), maximize (□), close (X) buttons
- Examples: "Untitled - Notepad", "Calculator", "Google Chrome", "Document1 - Word"

**Window Components to Check**:
1. **Menu Bar** (directly below title bar): File, Edit, View, Tools, Help, etc.
2. **Toolbar** (icons/buttons for common actions)
3. **Content Area** (main work area - white for text editors, varied for others)
4. **Status Bar** (bottom edge showing info like "Ln 1, Col 1", zoom level, etc.)

**Application-Specific Patterns**:
- **Text Editors** (Notepad, Word): White background, menu bar, text cursor, status bar
- **Calculators**: Number pad (0-9), operators (+, -, x, ÷), display area showing numbers
- **Browsers** (Chrome, Edge): Address bar with URL, tabs at top, navigation buttons (←, →, ⟳)
- **File Explorer**: Folder tree on left, file list on right, address bar showing path
- **Command Prompts/Terminals**: Black or dark background, monospace text, command line prompt

**Detection Strategy**:
1. Scan from TOP to BOTTOM of screen
2. Check each visible window's title bar for app names
3. Look for PARTIAL visibility - even 20% of a window counts as "visible"
4. Don't assume windows are hidden just because they're small or partially covered
5. Check the TASKBAR at bottom for open application icons

**Common Mistakes to Avoid**:
❌ "No window visible" when window is partially covered - WRONG!
✅ "Window visible but partially covered by another window" - CORRECT!
❌ Saying an app isn't open when you can see its title bar - WRONG!
✅ Recognizing any visible title bar or menu means that app IS OPEN - CORRECT!

**Task Execution Strategy**:
1. **Understand the Goal**: Break down what needs to be achieved
2. **Assess Current State**: What's already on screen? What's missing?
3. **Plan Minimal Steps**: Use the FEWEST actions to complete the task
4. **Adapt to Reality**: If something already exists, skip creating it
5. **Verify Progress**: Check if each action had the expected effect

**Smart Decision Making**:
- **PREFER MOUSE OVER COMMANDS**: Instead of open_app, click Start menu and search
- **Locate Visual Elements**: Find buttons, icons, links on screen and click them
- **Use Taskbar**: Click taskbar icons to switch between open applications
- **Estimate Coordinates**: Look at element positions and estimate x,y coordinates
- **Focus Windows**: Click on a window's title bar or content area to focus it
- **Navigate Naturally**: Use mouse like a human would - click buttons, links, icons
- **Verify Clicks Work**: If a click doesn't work, try a different coordinate nearby
- **Search for Apps**: Win+S or click Start → type app name → click result

**EXAMPLES OF PROPER MOUSE NAVIGATION**:
✅ "To open Notepad: mouse_click Start button (10, 1430) → keyboard_type 'notepad' → mouse_click first result"
✅ "To focus window: mouse_click on its title bar or visible content area"
✅ "To click button: estimate button center coordinates from visual inspection"
❌ "To open Notepad: open_app notepad" - USE MOUSE INSTEAD!

NOW: Look at the image, analyze the situation, think about the best approach, then respond with your thinking + JSON."""
                
                # Clear overlay and prepare for streaming tokens
                if self.overlay:
                    self.overlay.clear_reasoning()  # Clear so tokens start fresh
                
                # Validate model is set
                if not self.current_model:
                    logging.error("[Agent] No model set! Cannot generate response.")
                    execution_log.append(f"Step {step + 1}: No model selected")
                    break
                
                # Detect if using qwen3-vl (doesn't support streaming)
                use_streaming = "qwen3-vl" not in self.current_model.lower()
                
                # Enable streaming to show tokens as they're generated (except qwen3-vl)
                # Optimized for speed with lower temperature and shorter context
                payload = {
                    "model": self.current_model,
                    "prompt": prompt,
                    "images": [screenshot_base64],
                    "stream": use_streaming
                }
                
                # Add options only for non-qwen3-vl models
                if use_streaming:
                    payload["options"] = {
                        "num_ctx": 2048,  # Smaller context for faster generation
                        "num_gpu": 99,
                        "num_thread": 4,
                        "numa": False,
                        "temperature": 0.3,  # Lower temperature for more focused, faster responses
                        "top_p": 0.9,
                        "top_k": 40,
                        "num_predict": 512  # Limit max tokens for faster responses
                    }
                
                logging.info(f"[Agent] Sending request to Ollama...")
                logging.info(f"[Agent] Model: {self.current_model}")
                logging.info(f"[Agent] Prompt length: {len(prompt)} chars")
                logging.info(f"[Agent] Screenshot size: {len(screenshot_base64)} bytes")
                logging.info(f"[Agent] Streaming enabled: {use_streaming}")
                
                try:
                    response = requests.post(
                        f"{self.ollama.base_url}/api/generate",
                        json=payload,
                        timeout=60,
                        stream=use_streaming  # Disable streaming for qwen3-vl
                    )
                    
                    logging.info(f"[Agent] Response status: {response.status_code}")
                    logging.info(f"[Agent] Response headers: {dict(response.headers)}")
                    
                    if response.status_code == 200:
                        if use_streaming:
                            # Verify it's a streaming response
                            if not hasattr(response, 'iter_lines'):
                                logging.error("[Agent] Response object doesn't support iter_lines!")
                                result = {"success": False, "error": "Invalid streaming response object"}
                            else:
                                logging.info("[Agent] Valid streaming response received")
                                result = {"success": True, "response": response, "streaming": True}
                        else:
                            # Non-streaming response (qwen3-vl)
                            logging.info("[Agent] Non-streaming response received (qwen3-vl)")
                            response_json = response.json()
                            logging.info(f"[Agent] Response JSON keys: {response_json.keys()}")
                            response_text = response_json.get('response', '')
                            thinking = response_json.get('thinking', '')
                            logging.info(f"[Agent] Got {len(response_text)} chars from 'response' field")
                            logging.info(f"[Agent] Got {len(thinking)} chars from 'thinking' field")
                            if thinking and not response_text:
                                logging.warning("[Agent] Using 'thinking' field instead of 'response'")
                                response_text = thinking
                            result = {"success": True, "response_text": response_text, "streaming": False}
                    else:
                        error_msg = f"HTTP {response.status_code}: {response.text}"
                        logging.error(f"[Agent] Ollama error: {error_msg}")
                        result = {"success": False, "error": error_msg}
                except Exception as e:
                    logging.error(f"[Agent] Request exception: {e}")
                    import traceback
                    traceback.print_exc()
                    result = {"success": False, "error": str(e)}
                
                if not result["success"]:
                    execution_log.append(f"Step {step + 1}: AI generation failed: {result.get('error')}")
                    logging.error(f"AI generation failed: {result.get('error')}")
                    break
                
                # Handle streaming vs non-streaming responses
                response_text = ""
                
                if result.get("streaming"):
                    # Stream tokens and accumulate response
                    streaming_response = result.get("response")
                    
                    if not streaming_response:
                        logging.error("[Agent] No streaming response received")
                        logging.error(f"[Agent] Result contents: {result}")
                        execution_log.append(f"Step {step + 1}: No response from AI")
                        break
                    
                    logging.info(f"[Agent] Starting to stream tokens from: {type(streaming_response)}")
                    token_count = 0
                    lines_processed = 0
                    
                    try:
                        for line in streaming_response.iter_lines():
                            lines_processed += 1
                            
                            if self.cancel_requested:
                                break
                            
                            if line:
                                try:
                                    decoded_line = line.decode('utf-8')
                                    # Log first few raw lines for debugging
                                    if lines_processed <= 2:
                                        logging.info(f"[Agent] Raw line {lines_processed}: {decoded_line[:200]}")
                                    
                                    chunk = json.loads(decoded_line)
                                    
                                    # Debug: log first chunk structure
                                    if token_count == 0:
                                        logging.info(f"[Agent] First chunk keys: {chunk.keys()}")
                                    
                                    # Handle different model response formats
                                    token = None
                                    if 'response' in chunk and chunk['response']:
                                        token = chunk['response']
                                    elif 'thinking' in chunk and chunk['thinking']:
                                        # qwen3-vl puts output in 'thinking' field
                                        token = chunk['thinking']
                                    
                                    if token:
                                        response_text += token
                                        token_count += 1
                                        
                                        # Show token in overlay immediately
                                        if self.overlay:
                                            self.overlay.append_token(token)
                                        
                                        # Log first few tokens for debugging
                                        if token_count <= 3:
                                            logging.info(f"[Agent] Token {token_count}: '{token}'")
                                            
                                    # Check if generation is done
                                    if chunk.get('done', False):
                                        logging.info(f"[Agent] Streaming complete. Total tokens: {token_count}, Lines: {lines_processed}")
                                        break
                                except json.JSONDecodeError as e:
                                    logging.warning(f"Failed to parse streaming chunk: {line[:100]}")
                                    continue
                            else:
                                # Empty line received
                                if lines_processed <= 5:
                                    logging.debug(f"[Agent] Empty line at position {lines_processed}")
                        
                        # Log if loop completed without any lines
                        if lines_processed == 0:
                            logging.error("[Agent] No lines received from streaming response!")
                            
                    except Exception as e:
                        logging.error(f"Streaming error: {e}")
                        import traceback
                        traceback.print_exc()
                        execution_log.append(f"Step {step + 1}: Streaming failed: {str(e)}")
                        break
                else:
                    # Non-streaming (qwen3-vl) - already have response_text
                    response_text = result.get("response_text", "")
                    logging.info(f"[Agent] Non-streaming response: {len(response_text)} chars")
                    if self.overlay:
                        self.overlay.append_token(response_text)  # Show full response at once
                
                response_text = response_text.strip()
                
                if not response_text:
                    logging.error(f"[Agent] AI returned empty response")
                    execution_log.append(f"Step {step + 1}: AI returned empty response")
                    break
                
                logging.info(f"[Agent] Full AI Response ({len(response_text)} chars): {response_text[:500]}...")
                
                # Try to extract JSON from response (may contain thinking text before JSON)
                import re
                
                # First try to find JSON in code blocks (improved regex that handles nested content)
                json_block_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_block_match:
                    json_text = json_block_match.group(1)
                else:
                    # Try finding JSON without code block markers
                    # Look for pattern starting with { and ending with }, allowing nested braces
                    json_start = response_text.find('{')
                    if json_start != -1:
                        # Find the matching closing brace
                        brace_count = 0
                        in_string = False
                        escape_next = False
                        json_end = -1
                        
                        for i in range(json_start, len(response_text)):
                            char = response_text[i]
                            
                            if escape_next:
                                escape_next = False
                                continue
                            
                            if char == '\\':
                                escape_next = True
                                continue
                            
                            if char == '"' and not in_string:
                                in_string = True
                            elif char == '"' and in_string:
                                in_string = False
                            elif char == '{' and not in_string:
                                brace_count += 1
                            elif char == '}' and not in_string:
                                brace_count -= 1
                                if brace_count == 0:
                                    json_end = i + 1
                                    break
                        
                        if json_end != -1:
                            json_text = response_text[json_start:json_end]
                        else:
                            # AI didn't provide valid JSON, log what we got
                            logging.error(f"Invalid AI response (no JSON found): {response_text[:500]}")
                            execution_log.append(f"Step {step + 1}: Invalid AI response format")
                            execution_log.append(f"  AI said: {response_text[:200] if response_text else '(empty)'}...")
                            break
                    else:
                        # AI didn't provide valid JSON, log what we got
                        logging.error(f"Invalid AI response (no JSON found): {response_text[:500]}")
                        execution_log.append(f"Step {step + 1}: Invalid AI response format")
                        execution_log.append(f"  AI said: {response_text[:200] if response_text else '(empty)'}...")
                        break
                
                try:
                    action_plan = json.loads(json_text)
                    
                    # Log thinking if present
                    if "observation" in action_plan:
                        logging.info(f"[Agent] AI Observation: {action_plan['observation']}")
                    
                    logging.info(f"[Agent] Parsed action: {action_plan}")
                except json.JSONDecodeError as e:
                    logging.error(f"JSON parse error: {e}")
                    logging.error(f"Attempted to parse: {json_text[:200]}")
                    execution_log.append(f"Step {step + 1}: Could not parse AI response")
                    execution_log.append(f"  JSON found: {json_text[:100]}...")
                    break
                
                action_type = action_plan.get("action", "").lower()
                reasoning = action_plan.get("reasoning", "")
                observation = action_plan.get("observation", "")
                parameters = action_plan.get("parameters", {})
                task_complete = action_plan.get("task_complete", False)
                
                # Log observation if present
                if observation:
                    execution_log.append(f"  👁️ AI sees: {observation[:100]}")
                
                # Detect action loops (same action repeating)
                current_action = f"{action_type}_{parameters.get('app', parameters.get('text', ''))}"
                if current_action == last_action:
                    repeat_count += 1
                    if repeat_count >= 3:
                        logging.warning(f"[Agent] Detected action loop: {action_type} repeated {repeat_count} times")
                        execution_log.append(f"⚠ Warning: Action '{action_type}' repeated {repeat_count} times - AI may be stuck")
                        
                        # Generic auto-recovery: if stuck opening app, suggest moving on
                        if action_type == "open_app" and repeat_count >= 3:
                            logging.info(f"[Agent] Stuck opening app - it may already be open or failing to launch")
                            execution_log.append(f"⚠ App might already be open or unavailable - AI should check screen and adapt")
                        
                        # Break at 5 repetitions for any action type
                        if repeat_count >= 5:
                            logging.error(f"[Agent] Breaking out of infinite loop at step {step + 1}")
                            execution_log.append(f"❌ Stopped: AI stuck in loop repeating '{action_type}' - task may be impossible or complete")
                            break
                else:
                    repeat_count = 0
                    last_action = current_action
                
                execution_log.append(f"Step {step + 1}: {action_type} - {reasoning}")
                logging.info(f"[Agent] Step {step + 1}: {action_type} - {reasoning}")
                
                # Store action context for next iteration
                action_result = None
                
                # Execute the action if auto_execute is enabled
                if auto_execute:
                    if action_type == "complete" or task_complete:
                        execution_log.append("Task completed successfully!")
                        return {
                            "success": True,
                            "task": task,
                            "steps_completed": steps_completed,
                            "execution_log": execution_log,
                            "message": "Task completed!"
                        }
                    
                    elif action_type == "detect_ui_element":
                        # Use OpenCV to detect UI element and get exact coordinates
                        element_name = parameters.get("element_name", "")
                        if not element_name:
                            action_result = "Failed: No element_name provided"
                            execution_log.append("  Error: Must specify element_name")
                        else:
                            if self.overlay:
                                self.overlay.update_reasoning(f"🔍 Detecting UI element: {element_name}...")
                            
                            elements = self.ui_detector.detect_elements(screenshot_base64, element_query=element_name)
                            
                            if elements and len(elements) > 0:
                                elem = elements[0]
                                steps_completed += 1
                                
                                # Store coordinates for potential next action
                                self.last_detected_coords = (elem['x'], elem['y'])
                                
                                # Automatically move mouse to detected coordinates
                                move_result = self.task_executor.execute_mouse_move(
                                    elem['x'], 
                                    elem['y'], 
                                    duration=0.5
                                )
                                
                                if move_result["success"]:
                                    action_result = f"✓ Found '{elem['name']}' at ({elem['x']}, {elem['y']}) and moved mouse there"
                                    execution_log.append(f"✓ Detected: {elem['name']} at ({elem['x']}, {elem['y']})")
                                    execution_log.append(f"✓ Moved mouse to ({elem['x']}, {elem['y']})")
                                    
                                    # Show user the detected element and movement
                                    if self.overlay:
                                        self.overlay.update_reasoning(f"✓ Found {elem['name']} at ({elem['x']}, {elem['y']}) - Mouse moved!")
                                else:
                                    action_result = f"✓ Found '{elem['name']}' at ({elem['x']}, {elem['y']}) but mouse move failed"
                                    execution_log.append(f"✓ Detected: {elem['name']} at ({elem['x']}, {elem['y']})")
                                    execution_log.append(f"  Warning: Mouse move failed - {move_result.get('error', 'unknown error')}")
                            else:
                                action_result = f"Element '{element_name}' not found"
                                execution_log.append(f"  Could not find: {element_name}")
                                if self.overlay:
                                    self.overlay.update_reasoning(f"❌ Could not find '{element_name}'")
                    
                    elif action_type == "mouse_click":
                        result = self.task_executor.execute_mouse_click(
                            parameters.get("x", 0),
                            parameters.get("y", 0),
                            parameters.get("button", "left")
                        )
                        if result["success"]:
                            steps_completed += 1
                            action_result = f"Clicked at ({parameters.get('x', 0)}, {parameters.get('y', 0)})"
                            time.sleep(0.5)  # Brief pause after click
                        else:
                            action_result = f"Failed: {result['error']}"
                            execution_log.append(f"  Error: {result['error']}")
                    
                    elif action_type == "keyboard_type":
                        result = self.task_executor.execute_keyboard_type(
                            parameters.get("text", "")
                        )
                        if result["success"]:
                            steps_completed += 1
                            text_preview = parameters.get('text', '')[:50]
                            action_result = f"Typed: {text_preview}"
                            execution_log.append(f"✓ Typed: {parameters.get('text', '')}")
                            time.sleep(0.3)
                        else:
                            action_result = f"Failed: {result['error']}"
                            execution_log.append(f"  Error: {result['error']}")
                    
                    elif action_type == "key_press":
                        result = self.task_executor.execute_key_press(
                            parameters.get("key", "")
                        )
                        if result["success"]:
                            steps_completed += 1
                            time.sleep(0.3)
                        else:
                            execution_log.append(f"  Error: {result['error']}")
                    
                    elif action_type == "hotkey":
                        keys = parameters.get("keys", [])
                        if isinstance(keys, list) and keys:
                            result = self.task_executor.execute_hotkey(*keys)
                            if result["success"]:
                                steps_completed += 1
                                time.sleep(0.5)
                            else:
                                execution_log.append(f"  Error: {result['error']}")
                        else:
                            execution_log.append(f"  Error: Invalid hotkey parameters")
                    
                    elif action_type == "open_app":
                        app = parameters.get("app", "")
                        if app:
                            result = self.task_executor.open_application(app)
                            if result["success"]:
                                steps_completed += 1
                                action_result = f"Opened {app} successfully"
                                logging.info(f"[Agent] Successfully opened: {app}")
                                execution_log.append(f"  ✓ Opened {app}")
                                time.sleep(1.5)  # Give app time to open
                            else:
                                action_result = f"Failed to open {app}: {result['error']}"
                                logging.error(f"[Agent] Failed to open {app}: {result['error']}")
                                execution_log.append(f"  Error: {result['error']}")
                        else:
                            action_result = "Failed: No app specified"
                            execution_log.append(f"  Error: No app specified")
                    
                    elif action_type == "mouse_move":
                        result = self.task_executor.execute_mouse_move(
                            parameters.get("x", 0),
                            parameters.get("y", 0)
                        )
                        if result["success"]:
                            steps_completed += 1
                            time.sleep(0.2)
                        else:
                            execution_log.append(f"  Error: {result['error']}")
                    
                    elif action_type == "double_click":
                        result = self.task_executor.execute_double_click(
                            parameters.get("x", 0),
                            parameters.get("y", 0)
                        )
                        if result["success"]:
                            steps_completed += 1
                            time.sleep(0.5)
                        else:
                            execution_log.append(f"  Error: {result['error']}")
                    
                    elif action_type == "right_click":
                        result = self.task_executor.execute_right_click(
                            parameters.get("x", 0),
                            parameters.get("y", 0)
                        )
                        if result["success"]:
                            steps_completed += 1
                            time.sleep(0.5)
                        else:
                            execution_log.append(f"  Error: {result['error']}")
                    
                    elif action_type == "escape":
                        result = self.task_executor.execute_escape()
                        if result["success"]:
                            steps_completed += 1
                            time.sleep(0.3)
                        else:
                            execution_log.append(f"  Error: {result['error']}")
                    
                    elif action_type == "ctrl_n":
                        result = self.task_executor.execute_ctrl_n()
                        if result["success"]:
                            steps_completed += 1
                            time.sleep(0.7)
                        else:
                            execution_log.append(f"  Error: {result['error']}")
                    
                    elif action_type == "select_all":
                        result = self.task_executor.execute_select_all()
                        if result["success"]:
                            steps_completed += 1
                            time.sleep(0.2)
                        else:
                            execution_log.append(f"  Error: {result['error']}")
                    
                    elif action_type == "save_file":
                        result = self.task_executor.execute_save_file()
                        if result["success"]:
                            steps_completed += 1
                            time.sleep(0.3)
                        else:
                            execution_log.append(f"  Error: {result['error']}")
                    
                    elif action_type == "alt_tab":
                        result = self.task_executor.execute_alt_tab()
                        if result["success"]:
                            steps_completed += 1
                            time.sleep(0.5)
                        else:
                            execution_log.append(f"  Error: {result['error']}")
                    
                    elif action_type == "scroll":
                        result = self.task_executor.execute_scroll(
                            parameters.get("amount", 3)
                        )
                        if result["success"]:
                            steps_completed += 1
                            time.sleep(0.3)
                        else:
                            execution_log.append(f"  Error: {result['error']}")
                    
                    elif action_type == "wait":
                        wait_time = parameters.get("seconds", 1)
                        time.sleep(wait_time)
                        execution_log.append(f"  Waited {wait_time} seconds")
                    
                    else:
                        action_result = f"Unknown action: {action_type}"
                        execution_log.append(f"  Unknown action type: {action_type}")
                    
                    # Save this step to context for next iteration
                    task_context.append({
                        "step": step + 1,
                        "action": action_type,
                        "reasoning": reasoning,
                        "observation": observation,
                        "result": action_result
                    })
                    
                    # Overlay already hidden before action execution above
                    # Wait for screen to update after action
                    time.sleep(0.5)
                
                else:
                    # Manual mode - return the plan for user confirmation
                    return {
                        "success": True,
                        "task": task,
                        "action_plan": action_plan,
                        "execution_log": execution_log,
                        "message": "Action plan ready. Confirm to execute.",
                        "requires_confirmation": True
                    }
            
            # Max steps reached
            result = {
                "success": True,
                "task": task,
                "steps_completed": steps_completed,
                "execution_log": execution_log,
                "message": f"Task execution stopped after {max_steps} steps. May need manual completion."
            }
            
        except Exception as e:
            logging.error(f"[Agent] Task execution error: {e}")
            result = {
                "success": False,
                "error": str(e),
                "execution_log": execution_log
            }
        
        finally:
            # STOP overlay completely when done
            if self.overlay:
                self.overlay.update_reasoning("")
                self.overlay.stop()  # Completely stop the overlay window
            
            # Unload model from memory to prevent lag
            if self.current_model:
                logging.info("Unloading model to free memory...")
                self.ollama.unload_model(self.current_model)
            
            # Clean up old screenshots (keep last 10)
            self.screen_analyzer.cleanup_old_screenshots(keep_last=10)
            
            # Force garbage collection
            import gc
            gc.collect()
        
        return result
    
    def chat(self, message: str, include_screen: bool = False) -> Dict:
        """Chat with agent, optionally including screen context"""
        if not self.current_model:
            return {"success": False, "error": "No model selected"}
        
        # Build message
        user_message = {"role": "user", "content": message}
        messages = self.conversation_history + [user_message]
        
        # Optionally include screen
        images = None
        if include_screen:
            screenshot_base64 = self.screen_analyzer.capture_screen()
            if screenshot_base64:
                images = [screenshot_base64]
                user_message["content"] += " [Screen included]"
        
        # Get response from Ollama
        result = self.ollama.chat(
            model=self.current_model,
            messages=messages,
            images=images
        )
        
        if result["success"]:
            # Add to history
            self.conversation_history.append(user_message)
            self.conversation_history.append({
                "role": "assistant",
                "content": result["response"],
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "success": True,
                "response": result["response"],
                "screenshot": self.screen_analyzer.last_screenshot.name if include_screen else None
            }
        else:
            return result
    
    def set_permissions(self, permissions: Dict) -> Dict:
        """Set agent permissions"""
        for action_type, granted in permissions.items():
            self.task_executor.set_permission(action_type, granted)
        
        return {
            "success": True,
            "permissions": self.task_executor.permissions
        }
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "active": self.active,
            "model": self.current_model,
            "ollama_connected": self.ollama.check_connection(),
            "permissions": self.task_executor.permissions,
            "conversation_length": len(self.conversation_history),
            "action_history_length": len(self.task_executor.action_history),
            "screen_info": self.screen_analyzer.get_screen_info()
        }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.task_executor.action_history = []
        return {"success": True, "message": "History cleared"}
    
    def execute_action(self, action: Dict) -> Dict:
        """Execute a specific action"""
        action_type = action.get("type")
        
        if action_type == "mouse_click":
            return self.task_executor.execute_mouse_click(
                action["x"], action["y"], action.get("button", "left")
            )
        elif action_type == "keyboard_type":
            return self.task_executor.execute_keyboard_type(action["text"])
        elif action_type == "key_press":
            return self.task_executor.execute_key_press(action["key"])
        elif action_type == "mouse_move":
            return self.task_executor.execute_mouse_move(action["x"], action["y"])
        else:
            return {"success": False, "error": f"Unknown action type: {action_type}"}
