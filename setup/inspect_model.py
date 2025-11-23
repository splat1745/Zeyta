from chatterbox import ChatterboxTTS
import warnings
warnings.filterwarnings('ignore')

m = ChatterboxTTS.from_pretrained(device='cuda')
print('Has s3gen?', hasattr(m, 's3gen'))
if hasattr(m, 's3gen'):
    print('s3gen children:', [n for n, _ in m.s3gen.named_children()])
print('Has tokenizer?', hasattr(m, 'tokenizer'))
if hasattr(m, 'tokenizer'):
    print('tokenizer class:', m.tokenizer.__class__)
    print('tokenizer children:', [n for n, _ in m.tokenizer.named_children()])
print('Has ve?', hasattr(m, 've'))
if hasattr(m, 've'):
    print('ve children:', [n for n, _ in m.ve.named_children()])
