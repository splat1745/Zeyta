"""Monkey patch for older setuptools behavior on Python 3.12."""
import pkgutil
import zipimport

if not hasattr(pkgutil, "ImpImporter"):
    pkgutil.ImpImporter = zipimport.zipimporter
