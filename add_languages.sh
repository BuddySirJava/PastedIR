#!/bin/bash

# Script to add programming languages to the Django database
# Compatible with docker-compose.yml setup

set -e

echo "🚀 Starting language import process..."

# Check if we're in a Docker environment
if [ -f "docker-compose.yml" ]; then
    echo "📦 Detected Docker environment, using docker-compose"
    
    echo "🔧 Running language import in Django container..."
    # Execute the Python directly inside the container via stdin
    docker-compose exec -T django python - << 'EOF'
#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pastebinir.settings')
django.setup()

from website.models import Language

# Language data
languages_data = [
    # Major Programming Languages
    ("Python", "python"),
    ("JavaScript", "javascript"),
    ("Java", "java"),
    ("C++", "cpp"),
    ("C", "c"),
    ("C#", "csharp"),
    ("PHP", "php"),
    ("Ruby", "ruby"),
    ("Go", "go"),
    ("Rust", "rust"),
    ("Swift", "swift"),
    ("Kotlin", "kotlin"),
    ("TypeScript", "typescript"),
    ("Scala", "scala"),
    ("R", "r"),
    ("Dart", "dart"),
    ("Julia", "julia"),
    ("Elixir", "elixir"),
    ("Haskell", "haskell"),
    ("Clojure", "clojure"),
    ("F#", "fsharp"),
    ("OCaml", "ocaml"),
    ("Lua", "lua"),
    ("Perl", "perl"),
    ("Objective C", "objectivec"),
    ("Groovy", "groovy"),
    ("Crystal", "crystal"),
    ("Nim", "nim"),
    ("Zig", "zig"),
    
    # Web Technologies
    ("HTML, XML", "xml"),
    ("CSS", "css"),
    ("SCSS", "scss"),
    ("Less", "less"),
    ("Sass", "sass"),
    ("Handlebars", "handlebars"),
    ("Blade (Laravel)", "blade"),
    ("Twig", "twig"),
    ("Haml", "haml"),
    ("Pug", "pug"),
    ("Svelte", "svelte"),
    ("Vue", "vue"),
    ("JSX", "jsx"),
    ("TSX", "tsx"),
    
    # Scripting & Shell
    ("Bash", "bash"),
    ("Shell", "shell"),
    ("PowerShell", "powershell"),
    ("Python REPL", "python-repl"),
    ("Awk", "awk"),
    ("Sed", "sed"),
    ("Makefile", "makefile"),
    ("Dockerfile", "dockerfile"),
    ("YAML", "yml"),
    ("TOML", "toml"),
    ("INI", "ini"),
    ("JSON", "json"),
    ("XML", "xml"),
    ("CSV", "csv"),
    
    # Database & Query Languages
    ("SQL", "sql"),
    ("PostgreSQL & PL/pgSQL", "pgsql"),
    ("MySQL", "mysql"),
    ("Transact-SQL", "tsql"),
    ("PL/SQL", "plsql"),
    ("GraphQL", "graphql"),
    ("MongoDB", "mongodb"),
    ("Redis", "redis"),
    
    # Configuration & Markup
    ("Markdown", "markdown"),
    ("AsciiDoc", "asciidoc"),
    ("reStructuredText", "rst"),
    ("LaTeX", "tex"),
    ("Diff", "diff"),
    ("Git", "git"),
    ("Nginx", "nginx"),
    ("Apache", "apache"),
    ("Iptables", "iptables"),
    ("Systemd", "systemd"),
    
    # Assembly & Low-level
    ("x86 Assembly", "x86asm"),
    ("ARM Assembly", "armasm"),
    ("RISC-V Assembly", "riscv"),
    ("MIPS Assembly", "mips"),
    ("LLVM IR", "llvm"),
    ("WebAssembly", "wasm"),
    
    # Mobile & Embedded
    ("Arduino", "arduino"),
    ("Processing", "processing"),
    ("OpenGL Shading Language", "glsl"),
    ("HLSL", "hlsl"),
    ("CUDA", "cuda"),
    ("OpenCL", "opencl"),
    
    # Data Science & ML
    ("Jupyter Notebook", "jupyter"),
    ("R", "r"),
    ("MATLAB", "matlab"),
    ("Octave", "octave"),
    ("Sage", "sage"),
    ("Stata", "stata"),
    ("SAS", "sas"),
    ("SPSS", "spss"),
    
    # Functional & Academic
    ("Haskell", "haskell"),
    ("OCaml", "ocaml"),
    ("F#", "fsharp"),
    ("Erlang", "erlang"),
    ("Elixir", "elixir"),
    ("Clojure", "clojure"),
    ("Scheme", "scheme"),
    ("Lisp", "lisp"),
    ("Coq", "coq"),
    ("Agda", "agda"),
    ("Idris", "idris"),
    
    # Blockchain & Smart Contracts
    ("Solidity", "solidity"),
    ("Vyper", "vyper"),
    ("Move", "move"),
    ("Cadence", "cadence"),
    
    # DevOps & Infrastructure
    ("Terraform", "terraform"),
    ("Ansible", "ansible"),
    ("Puppet", "puppet"),
    ("Chef", "chef"),
    ("Salt", "salt"),
    ("Kubernetes", "kubernetes"),
    ("Helm", "helm"),
    ("Prometheus", "prometheus"),
    ("Grafana", "grafana"),
    
    # Testing & Documentation
    ("Gherkin", "gherkin"),
    ("Cucumber", "cucumber"),
    ("Robot Framework", "robot"),
    ("Jest", "jest"),
    ("Mocha", "mocha"),
    ("Jasmine", "jasmine"),
    ("Cypress", "cypress"),
    ("Selenium", "selenium"),
    
    # Legacy & Enterprise
    ("COBOL", "cobol"),
    ("Fortran", "fortran"),
    ("Pascal", "pascal"),
    ("Delphi", "delphi"),
    ("Visual Basic", "vb"),
    ("VBA", "vba"),
    ("VBScript", "vbscript"),
    ("ABAP", "abap"),
    ("PL/I", "pli"),
    ("Ada", "ada"),
    
    # Specialized & Domain-specific
    ("Verilog", "verilog"),
    ("VHDL", "vhdl"),
    ("SystemVerilog", "systemverilog"),
    ("Chisel", "chisel"),
    ("SpinalHDL", "spinalhdl"),
    ("Mermaid", "mermaid"),
    ("PlantUML", "plantuml"),
    ("Graphviz", "dot"),
    ("Gnuplot", "gnuplot"),
    ("Matplotlib", "matplotlib"),
    
    # Plain text and misc
    ("Plaintext", "plaintext"),
    ("Text", "text"),
    ("Log", "log"),
    ("Access Log", "accesslog"),
    ("Error Log", "errorlog"),
    ("HTTP", "http"),
    ("cURL", "curl"),
    ("REST", "rest"),
    ("SOAP", "soap"),
    ("WSDL", "wsdl"),
]

def add_languages():
    """Add languages to the database"""
    created_count = 0
    skipped_count = 0
    
    for displayname, alias in languages_data:
        # Skip languages with empty alias (like "Lang")
        if not alias.strip():
            print(f"⚠️  Skipping '{displayname}' - no alias provided")
            skipped_count += 1
            continue
            
        # Check if language already exists
        if Language.objects.filter(alias=alias).exists():
            print(f"⏭️  Skipping '{displayname}' ({alias}) - already exists")
            skipped_count += 1
            continue
            
        # Create the language
        try:
            Language.objects.create(displayname=displayname, alias=alias)
            print(f"✅ Added: {displayname} ({alias})")
            created_count += 1
        except Exception as e:
            print(f"❌ Error adding {displayname}: {e}")
    
    return created_count, skipped_count

if __name__ == "__main__":
    print("🗃️  Adding programming languages to database...")
    created, skipped = add_languages()
    print(f"\n📊 Summary:")
    print(f"   ✅ Created: {created} languages")
    print(f"   ⏭️  Skipped: {skipped} languages")
    print(f"   📝 Total processed: {created + skipped} languages")
    # Invalidate cached languages so UI sees updates immediately
    try:
        from django.core.cache import cache
        from django.conf import settings
        cache.delete(getattr(settings, 'LANGUAGE_CACHE_KEY', 'all_languages'))
        print("🧹 Cleared language cache key")
    except Exception as e:
        print(f"⚠️  Could not clear language cache: {e}")
EOF
    
else
    echo "❌ Error: docker-compose.yml not found in current directory"
    echo "   Please run this script from the project root directory"
    exit 1
fi

echo "🎉 Language import completed!"
