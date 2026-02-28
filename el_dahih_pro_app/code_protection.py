"""
Code protection and obfuscation utilities
"""
import os
import hashlib
import logging
import base64
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CodeProtection:
    """Protects application code from tampering and reverse engineering"""
    
    @staticmethod
    def generate_file_hash(file_path: str, algorithm='sha256') -> str:
        """Generate hash of a file for integrity verification"""
        try:
            hash_obj = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Error generating file hash: {e}")
            return None
    
    @staticmethod
    def verify_file_integrity(file_path: str, expected_hash: str, algorithm='sha256') -> bool:
        """Verify file integrity using hash"""
        try:
            actual_hash = CodeProtection.generate_file_hash(file_path, algorithm)
            
            if actual_hash is None:
                return False
            
            return actual_hash == expected_hash
        except Exception as e:
            logger.error(f"Error verifying file integrity: {e}")
            return False
    
    @staticmethod
    def create_manifest(directory: str) -> dict:
        """Create integrity manifest for directory"""
        manifest = {
            'created': datetime.now().isoformat(),
            'files': {}
        }
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(('.py', '.kv', '.json')):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, directory)
                        file_hash = CodeProtection.generate_file_hash(file_path)
                        
                        if file_hash:
                            manifest['files'][relative_path] = {
                                'hash': file_hash,
                                'size': os.path.getsize(file_path),
                                'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                            }
            
            logger.info(f"Manifest created with {len(manifest['files'])} files")
            return manifest
        except Exception as e:
            logger.error(f"Error creating manifest: {e}")
            return manifest
    
    @staticmethod
    def verify_manifest(directory: str, manifest: dict) -> bool:
        """Verify directory against manifest"""
        try:
            for file_path, file_info in manifest.get('files', {}).items():
                full_path = os.path.join(directory, file_path)
                
                if not os.path.exists(full_path):
                    logger.warning(f"File missing: {file_path}")
                    return False
                
                expected_hash = file_info.get('hash')
                actual_hash = CodeProtection.generate_file_hash(full_path)
                
                if actual_hash != expected_hash:
                    logger.warning(f"File modified: {file_path}")
                    return False
            
            logger.info("Manifest verification successful")
            return True
        except Exception as e:
            logger.error(f"Error verifying manifest: {e}")
            return False
    
    @staticmethod
    def obfuscate_string(text: str) -> str:
        """Simple string obfuscation"""
        try:
            encoded = base64.b64encode(text.encode()).decode()
            return f"OBFUSCATED_{encoded}"
        except Exception as e:
            logger.error(f"Error obfuscating string: {e}")
            return text
    
    @staticmethod
    def deobfuscate_string(obfuscated: str) -> str:
        """Deobfuscate string"""
        try:
            if obfuscated.startswith("OBFUSCATED_"):
                encoded = obfuscated.replace("OBFUSCATED_", "")
                return base64.b64decode(encoded).decode()
            return obfuscated
        except Exception as e:
            logger.error(f"Error deobfuscating string: {e}")
            return obfuscated
    
    @staticmethod
    def protect_sensitive_data(data: dict) -> dict:
        """Protect sensitive data in configuration"""
        protected = data.copy()
        
        sensitive_keys = ['password', 'token', 'secret', 'key', 'api_key']
        
        for key in sensitive_keys:
            if key in protected:
                protected[key] = CodeProtection.obfuscate_string(str(protected[key]))
        
        return protected
    
    @staticmethod
    def unprotect_sensitive_data(protected: dict) -> dict:
        """Unprotect sensitive data"""
        unprotected = protected.copy()
        
        sensitive_keys = ['password', 'token', 'secret', 'key', 'api_key']
        
        for key in sensitive_keys:
            if key in unprotected and isinstance(unprotected[key], str):
                if unprotected[key].startswith("OBFUSCATED_"):
                    unprotected[key] = CodeProtection.deobfuscate_string(unprotected[key])
        
        return unprotected


class DebugProtection:
    """Prevents debugging and reverse engineering"""
    
    @staticmethod
    def disable_debugging():
        """Disable debugging features"""
        try:
            import sys
            
            # Disable pdb
            sys.pdb = None
            
            # Disable traceback
            sys.tracebacklimit = 0
            
            logger.info("Debugging disabled")
            return True
        except Exception as e:
            logger.error(f"Error disabling debugging: {e}")
            return False
    
    @staticmethod
    def hide_source_code():
        """Hide source code from inspection"""
        try:
            import sys
            
            # Remove source code from modules
            for module in sys.modules.values():
                if hasattr(module, '__file__'):
                    module.__file__ = None
            
            logger.info("Source code hidden")
            return True
        except Exception as e:
            logger.error(f"Error hiding source code: {e}")
            return False
    
    @staticmethod
    def check_debugger():
        """Check if debugger is attached"""
        try:
            import sys
            
            # Check for debugger
            if hasattr(sys, 'debugger') or hasattr(sys, 'gettrace'):
                trace_func = sys.gettrace()
                if trace_func is not None:
                    logger.warning("Debugger detected")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking debugger: {e}")
            return False


class IntegrityChecker:
    """Checks application integrity"""
    
    def __init__(self, app_dir: str):
        self.app_dir = app_dir
        self.manifest = None
        self.last_check = None
    
    def create_integrity_manifest(self):
        """Create integrity manifest"""
        self.manifest = CodeProtection.create_manifest(self.app_dir)
        return self.manifest
    
    def verify_integrity(self) -> bool:
        """Verify application integrity"""
        if self.manifest is None:
            logger.warning("No manifest available")
            return False
        
        is_valid = CodeProtection.verify_manifest(self.app_dir, self.manifest)
        self.last_check = datetime.now()
        
        return is_valid
    
    def save_manifest(self, file_path: str) -> bool:
        """Save manifest to file"""
        try:
            if self.manifest is None:
                self.create_integrity_manifest()
            
            with open(file_path, 'w') as f:
                json.dump(self.manifest, f, indent=2)
            
            logger.info(f"Manifest saved to: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving manifest: {e}")
            return False
    
    def load_manifest(self, file_path: str) -> bool:
        """Load manifest from file"""
        try:
            with open(file_path, 'r') as f:
                self.manifest = json.load(f)
            
            logger.info(f"Manifest loaded from: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading manifest: {e}")
            return False
    
    def periodic_check(self, interval_seconds: int = 3600) -> bool:
        """Perform periodic integrity check"""
        if self.last_check is None:
            return self.verify_integrity()
        
        elapsed = (datetime.now() - self.last_check).total_seconds()
        
        if elapsed >= interval_seconds:
            return self.verify_integrity()
        
        return True


class SourceCodeProtection:
    """Protects Python source code"""
    
    @staticmethod
    def compile_to_bytecode(py_file: str, output_dir: str = None) -> bool:
        """Compile Python file to bytecode"""
        try:
            import py_compile
            
            if output_dir is None:
                output_dir = os.path.dirname(py_file)
            
            py_compile.compile(py_file, cfile=os.path.join(output_dir, '__pycache__'), doraise=True)
            
            logger.info(f"Compiled to bytecode: {py_file}")
            return True
        except Exception as e:
            logger.error(f"Error compiling to bytecode: {e}")
            return False
    
    @staticmethod
    def remove_source_files(directory: str, keep_backup: bool = True) -> bool:
        """Remove Python source files after compilation"""
        try:
            removed_count = 0
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        file_path = os.path.join(root, file)
                        
                        if keep_backup:
                            backup_path = file_path + '.bak'
                            os.rename(file_path, backup_path)
                        else:
                            os.remove(file_path)
                        
                        removed_count += 1
            
            logger.info(f"Removed {removed_count} source files")
            return True
        except Exception as e:
            logger.error(f"Error removing source files: {e}")
            return False
    
    @staticmethod
    def encrypt_source_files(directory: str, password: str) -> bool:
        """Encrypt Python source files"""
        try:
            from encryption_utils import EncryptionManager
            
            encrypted_count = 0
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        output_path = file_path + '.encrypted'
                        
                        if EncryptionManager.encrypt_file(file_path, output_path, password):
                            encrypted_count += 1
            
            logger.info(f"Encrypted {encrypted_count} source files")
            return True
        except Exception as e:
            logger.error(f"Error encrypting source files: {e}")
            return False
