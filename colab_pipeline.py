"""
NoemaKernel - Google Colab Pipeline
====================================

Setup and execution pipeline for running NoemaKernel in Google Colab environment.
Handles environment setup, dependencies, and provides convenient utilities.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class ColabSetup:
    """Setup utilities for Google Colab environment."""
    
    def __init__(self):
        self.is_colab = self._check_colab()
        self.project_root = Path.cwd()
        
    def _check_colab(self) -> bool:
        """Check if running in Google Colab."""
        try:
            import google.colab
            return True
        except ImportError:
            return False
    
    def setup_environment(self, clone_url: str = "https://github.com/omega-Core-Dev/NoemaKernel.git") -> bool:
        """
        Setup NoemaKernel in Colab environment.
        
        Args:
            clone_url: Repository URL to clone
            
        Returns:
            bool: True if setup successful
        """
        print("🔧 Setting up NoemaKernel in Colab...")
        
        try:
            if self.is_colab:
                self._setup_colab_env(clone_url)
            else:
                print("ℹ️  Not running in Colab. Using local environment.")
                if not Path("noemakernel").exists():
                    self._clone_repo(clone_url)
            
            print("✅ Environment setup complete!")
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    def _setup_colab_env(self, clone_url: str):
        """Setup Colab-specific environment."""
        # Mount Google Drive
        try:
            from google.colab import drive
            drive.mount('/content/drive')
            print("✅ Google Drive mounted")
        except:
            print("⚠️  Google Drive mount skipped")
        
        # Clone repository
        self._clone_repo(clone_url)
        
        # Add to path
        sys.path.insert(0, str(Path.cwd() / "NoemaKernel"))
        
        # Install any requirements
        self._install_requirements()
    
    def _clone_repo(self, url: str):
        """Clone the repository."""
        if not Path("NoemaKernel").exists():
            print(f"📥 Cloning {url}...")
            subprocess.run(["git", "clone", url], check=True)
            os.chdir("NoemaKernel")
            self.project_root = Path.cwd()
        else:
            os.chdir("NoemaKernel")
            self.project_root = Path.cwd()
    
    def _install_requirements(self):
        """Install Python dependencies."""
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            print("📦 Installing requirements...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)], 
                         capture_output=True)
        else:
            print("ℹ️  No requirements.txt found (using stdlib only)")


class NoemaKernelPipeline:
    """Main pipeline for NoemaKernel operations."""
    
    def __init__(self):
        """Initialize the pipeline."""
        self.setup = ColabSetup()
        self._ensure_imports()
    
    def _ensure_imports(self):
        """Ensure required modules are importable."""
        try:
            # Try to import NoemaKernel components
            sys.path.insert(0, str(self.setup.project_root))
        except:
            pass
    
    def run_basic_demo(self) -> Dict[str, Any]:
        """
        Run basic Bankmap demo.
        
        Returns:
            Dict with results
        """
        print("\n🚀 Running Basic Demo...")
        
        try:
            from noemakernel import BankmapEngine, ContextItem
            from noemakernel.context_judge import ContextJudge
            
            # Create sample contexts
            contexts = [
                ContextItem("c1", "Bankmap preserves semantic anchors."),
                ContextItem("c2", "Context routing improves LLM efficiency."),
                ContextItem("c3", "Semantic Sustainment Score guides decisions."),
            ]
            
            objective = "Route useful context before inference."
            
            # Run Bankmap
            engine = BankmapEngine()
            packet = engine.build_packet(contexts, objective)
            
            # Judge contexts
            judge = ContextJudge(profile="llm_continuous")
            results = []
            
            for ctx in contexts:
                result = judge.judge_context(ctx, objective, {"future_contexts": []})
                results.append({
                    "context_id": ctx.id,
                    "decision": result.to_dict()["decision"],
                    "score": result.to_dict().get("judge_score", 0)
                })
            
            output = {
                "status": "success",
                "compact_context": packet.compact_context if hasattr(packet, 'compact_context') else "Generated",
                "context_judgments": results,
                "timestamp": str(Path.cwd())
            }
            
            print("✅ Demo completed successfully!")
            return output
            
        except ImportError as e:
            print(f"⚠️  Import error (expected in setup): {e}")
            return {"status": "import_pending", "message": "Imports not yet available"}
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def run_tests(self) -> Dict[str, Any]:
        """
        Run NoemaKernel test suite.
        
        Returns:
            Dict with test results
        """
        print("\n🧪 Running Tests...")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                cwd=self.setup.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = {
                "status": "success" if result.returncode == 0 else "failed",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
            
            if result.returncode == 0:
                print("✅ All tests passed!")
            else:
                print("❌ Some tests failed")
            
            return output
            
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Tests exceeded time limit"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def run_stress_test(self, test_type: str = "bankmap") -> Dict[str, Any]:
        """
        Run stress tests.
        
        Args:
            test_type: Type of stress test (bankmap, context_judge, bidirectional, reactivation)
            
        Returns:
            Dict with results
        """
        print(f"\n⚡ Running {test_type} Stress Test...")
        
        test_scripts = {
            "bankmap": "examples/run_stress_test.py",
            "context_judge": "examples/run_context_judge_test.py",
            "bidirectional": "examples/run_bidirectional_test.py",
            "reactivation": "examples/run_reactivation_test.py",
            "modes": "examples/compare_bankmap_modes.py"
        }
        
        script = test_scripts.get(test_type)
        if not script:
            return {"status": "error", "message": f"Unknown test type: {test_type}"}
        
        script_path = self.setup.project_root / script
        if not script_path.exists():
            return {"status": "error", "message": f"Script not found: {script}"}
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.setup.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Test exceeded time limit"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def generate_artifacts(self) -> Dict[str, Any]:
        """Generate analysis artifacts."""
        print("\n📊 Generating Artifacts...")
        
        try:
            subprocess.run(
                [sys.executable, "examples/generate_chatgpt_prompts.py"],
                cwd=self.setup.project_root,
                capture_output=True,
                timeout=60
            )
            
            artifacts_dir = self.setup.project_root / "artifacts"
            artifacts = {}
            
            if artifacts_dir.exists():
                for f in artifacts_dir.rglob("*"):
                    if f.is_file():
                        artifacts[f.name] = str(f.relative_to(self.setup.project_root))
            
            return {
                "status": "success",
                "artifacts": artifacts,
                "location": str(artifacts_dir)
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def list_examples(self) -> List[str]:
        """List available examples."""
        examples_dir = self.setup.project_root / "examples"
        if examples_dir.exists():
            return [f.name for f in examples_dir.glob("*.py")]
        return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get pipeline status."""
        return {
            "is_colab": self.setup.is_colab,
            "project_root": str(self.setup.project_root),
            "examples_available": self.list_examples(),
            "artifacts_dir": str(self.setup.project_root / "artifacts")
        }


# ============================================================================
# COLAB QUICK START
# ============================================================================

def colab_quickstart():
    """Quick start for Colab notebook."""
    
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║        🚀 NoemaKernel - Google Colab Pipeline Setup 🚀        ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize pipeline
    pipeline = NoemaKernelPipeline()
    
    # Setup environment
    if not pipeline.setup.setup_environment():
        print("❌ Setup failed. Exiting.")
        return None
    
    # Print status
    status = pipeline.get_status()
    print("\n📊 Pipeline Status:")
    print(f"  • Colab Environment: {'Yes' if status['is_colab'] else 'No'}")
    print(f"  • Project Root: {status['project_root']}")
    print(f"  • Available Examples: {len(status['examples_available'])}")
    
    return pipeline


# ============================================================================
# USAGE IN COLAB
# ============================================================================

if __name__ == "__main__":
    # For local testing
    pipeline = NoemaKernelPipeline()
    pipeline.setup.setup_environment()
    
    print("\n📝 Pipeline ready. Available commands:")
    print("  • pipeline.run_basic_demo()")
    print("  • pipeline.run_tests()")
    print("  • pipeline.run_stress_test(test_type='bankmap')")
    print("  • pipeline.generate_artifacts()")
    print("  • pipeline.get_status()")
