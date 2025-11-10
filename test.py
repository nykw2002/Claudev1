#!/usr/bin/env python3
"""
File Analyzer with Anthropic API Integration

This script replicates the file analysis capabilities demonstrated earlier,
allowing users to upload files and ask questions about them using the Anthropic API
with tool calling functionality.

Requirements:
- anthropic>=0.34.0
- python-dotenv (optional, for environment variables)

Usage:
    python file_analyzer.py --question "How many complaints are from Israel?"
    python file_analyzer.py --interactive
    python file_analyzer.py --prompt "Custom prompt here"
"""

import os
import sys
import argparse
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

# HARDCODED SETTINGS - EDIT THESE
DEFAULT_FILE = "test.txt"  # Change this to your file path
DEFAULT_API_KEY = ""  # Change this to your API key

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


# Built-in configuration - modify these as needed
DEFAULT_FILE = "test.txt"  # Default file to analyze
DEFAULT_API_KEY = "your-anthropic-api-key-here"  # Replace with your actual API key


class FileAnalyzer:
    """Main class for analyzing files using Anthropic API with tool calling."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the FileAnalyzer with Anthropic API key."""
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set or not provided")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.working_dir = tempfile.mkdtemp(prefix='file_analyzer_')
        self.uploaded_files = {}
        
    def __del__(self):
        """Clean up temporary directory."""
        if hasattr(self, 'working_dir') and os.path.exists(self.working_dir):
            shutil.rmtree(self.working_dir)
    
    def upload_file(self, file_path: str) -> str:
        """Upload a file to the working directory and return its content."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Copy file to working directory
        filename = os.path.basename(file_path)
        dest_path = os.path.join(self.working_dir, filename)
        shutil.copy2(file_path, dest_path)
        
        # Read file content
        try:
            with open(dest_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(dest_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        self.uploaded_files[filename] = {
            'path': dest_path,
            'content': content,
            'size': len(content)
        }
        
        return content
    
    def define_tools(self) -> List[Dict[str, Any]]:
        """Define the tools available for the assistant."""
        return [
            {
                "name": "view_file",
                "description": "Read and view the contents of an uploaded file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the file to view"
                        },
                        "line_range": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Optional line range [start, end] to view specific lines"
                        }
                    },
                    "required": ["filename"]
                }
            },
            {
                "name": "search_text",
                "description": "Search for text patterns in uploaded files using grep-like functionality",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the file to search in"
                        },
                        "pattern": {
                            "type": "string",
                            "description": "Text pattern to search for (supports regex)"
                        },
                        "case_sensitive": {
                            "type": "boolean",
                            "description": "Whether the search should be case sensitive",
                            "default": False
                        },
                        "count_only": {
                            "type": "boolean",
                            "description": "If true, return only the count of matches",
                            "default": False
                        }
                    },
                    "required": ["filename", "pattern"]
                }
            },
            {
                "name": "run_command",
                "description": "Execute shell commands for advanced file analysis",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Shell command to execute"
                        },
                        "filename": {
                            "type": "string",
                            "description": "Name of the file to operate on (optional)"
                        }
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "analyze_data",
                "description": "Perform statistical analysis on found data patterns",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "data_type": {
                            "type": "string",
                            "enum": ["count", "frequency", "summary"],
                            "description": "Type of analysis to perform"
                        },
                        "data": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Data to analyze"
                        }
                    },
                    "required": ["data_type", "data"]
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return the result."""
        try:
            if tool_name == "view_file":
                return self._view_file(tool_input)
            elif tool_name == "search_text":
                return self._search_text(tool_input)
            elif tool_name == "run_command":
                return self._run_command(tool_input)
            elif tool_name == "analyze_data":
                return self._analyze_data(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def _view_file(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """View file contents."""
        filename = tool_input["filename"]
        line_range = tool_input.get("line_range")
        
        if filename not in self.uploaded_files:
            return {"error": f"File not found: {filename}"}
        
        content = self.uploaded_files[filename]["content"]
        lines = content.split('\n')
        
        if line_range:
            start, end = line_range
            start = max(1, start) - 1  # Convert to 0-based indexing
            end = min(len(lines), end)
            lines = lines[start:end]
            content = '\n'.join(f"{i+start+1:5d}\t{line}" for i, line in enumerate(lines))
        else:
            # For large files, show first and last parts
            if len(lines) > 100:
                first_50 = lines[:50]
                last_50 = lines[-50:]
                content = '\n'.join(f"{i+1:5d}\t{line}" for i, line in enumerate(first_50))
                content += f"\n... [truncated {len(lines)-100} lines] ...\n"
                content += '\n'.join(f"{len(lines)-50+i+1:5d}\t{line}" for i, line in enumerate(last_50))
            else:
                content = '\n'.join(f"{i+1:5d}\t{line}" for i, line in enumerate(lines))
        
        return {
            "content": content,
            "total_lines": len(self.uploaded_files[filename]["content"].split('\n')),
            "file_size": self.uploaded_files[filename]["size"]
        }
    
    def _search_text(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Search for text patterns in files."""
        filename = tool_input["filename"]
        pattern = tool_input["pattern"]
        case_sensitive = tool_input.get("case_sensitive", False)
        count_only = tool_input.get("count_only", False)
        
        if filename not in self.uploaded_files:
            return {"error": f"File not found: {filename}"}
        
        content = self.uploaded_files[filename]["content"]
        flags = 0 if case_sensitive else re.IGNORECASE
        
        try:
            matches = re.findall(pattern, content, flags)
            
            if count_only:
                return {"count": len(matches)}
            
            # Find lines containing matches
            lines = content.split('\n')
            matching_lines = []
            for i, line in enumerate(lines):
                if re.search(pattern, line, flags):
                    matching_lines.append(f"Line {i+1}: {line.strip()}")
            
            return {
                "matches": matches,
                "matching_lines": matching_lines,
                "count": len(matches),
                "line_count": len(matching_lines)
            }
        except re.error as e:
            return {"error": f"Invalid regex pattern: {str(e)}"}
    
    def _run_command(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute shell commands."""
        command = tool_input["command"]
        filename = tool_input.get("filename")
        
        # Security: Only allow safe commands
        safe_commands = ['grep', 'wc', 'head', 'tail', 'cat', 'sort', 'uniq', 'awk', 'sed']
        cmd_parts = command.split()
        if not cmd_parts or cmd_parts[0] not in safe_commands:
            return {"error": f"Command not allowed: {cmd_parts[0] if cmd_parts else 'empty command'}"}
        
        # Replace filename placeholder if provided
        if filename and filename in self.uploaded_files:
            file_path = self.uploaded_files[filename]["path"]
            command = command.replace("$FILE", file_path)
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except Exception as e:
            return {"error": f"Command execution failed: {str(e)}"}
    
    def _analyze_data(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Perform statistical analysis on data."""
        data_type = tool_input["data_type"]
        data = tool_input["data"]
        
        if data_type == "count":
            return {"count": len(data), "unique_count": len(set(data))}
        elif data_type == "frequency":
            freq = {}
            for item in data:
                freq[item] = freq.get(item, 0) + 1
            return {"frequency": freq, "total": len(data)}
        elif data_type == "summary":
            return {
                "total_items": len(data),
                "unique_items": len(set(data)),
                "sample": data[:5] if len(data) > 5 else data
            }
        else:
            return {"error": f"Unknown analysis type: {data_type}"}
    
    def ask_question(self, question: str, file_content: str = None, custom_prompt: str = None) -> str:
        """Ask a question about the uploaded files using the Anthropic API."""
        # Prepare system message
        if custom_prompt:
            system_message = custom_prompt
        else:
            system_message = """You are a file analysis assistant with access to tools for examining uploaded files. 
            You can view file contents, search for patterns, run shell commands, and analyze data.
            
            The user has uploaded a file and you have access to these tools:
            - view_file: Read and view file contents (use the filename provided by the user)
            - search_text: Search for text patterns in the file
            - run_command: Execute safe shell commands for analysis
            - analyze_data: Perform statistical analysis on found data
            
            IMPORTANT: Always follow this systematic 4-step approach for thorough analysis:
            1. FIRST: Use view_file to examine the file structure and understand the data format
            2. SECOND: Use search_text to find relevant patterns and information
            3. THIRD: Use run_command or additional searches to count and verify results
            4. FOURTH: Provide detailed analysis with specific numbers and context
            
            Make multiple tool calls to ensure accuracy. Never rely on a single search - always verify your findings through multiple approaches. The filename will be provided in the user's question."""
        
        # Prepare messages
        messages = []
        
        # Add file context if provided
        if file_content:
            messages.append({
                "role": "user",
                "content": f"I've uploaded a file with the following content preview:\n\n{file_content[:2000]}{'...' if len(file_content) > 2000 else ''}\n\nQuestion: {question}"
            })
        else:
            messages.append({
                "role": "user",
                "content": f"Question: {question}"
            })
        
        # Make API call with tools
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                system=system_message,
                messages=messages,
                tools=self.define_tools(),
                tool_choice={"type": "auto"}
            )
            
            # Handle tool calls
            final_response = ""
            current_messages = messages.copy()
            
            while response.stop_reason == "tool_use":
                # Process tool calls
                tool_results = []
                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_result = self.execute_tool(
                            content_block.name,
                            content_block.input
                        )
                        tool_results.append({
                            "tool_use_id": content_block.id,
                            "content": json.dumps(tool_result)
                        })
                
                # Add assistant's response to conversation
                current_messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                # Add tool results
                current_messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": result["tool_use_id"],
                            "content": result["content"]
                        } for result in tool_results
                    ]
                })
                
                # Continue conversation
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4000,
                    system=system_message,
                    messages=current_messages,
                    tools=self.define_tools(),
                    tool_choice={"type": "auto"}
                )
            
            # Extract final response
            for content_block in response.content:
                if content_block.type == "text":
                    final_response += content_block.text
            
            return final_response
            
        except Exception as e:
            return f"Error: {str(e)}"


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Analyze files using Anthropic API")
    parser.add_argument("--file", default=DEFAULT_FILE, help=f"Path to the file to analyze (default: {DEFAULT_FILE})")
    parser.add_argument("--question", help="Question to ask about the file")
    parser.add_argument("--prompt", help="Custom system prompt to override default file analysis behavior")
    parser.add_argument("--interactive", "-i", action="store_true", help="Enter interactive mode to type custom prompt")
    parser.add_argument("--api-key", default=DEFAULT_API_KEY, help="Anthropic API key (default: hardcoded)")
    
    args = parser.parse_args()
    
    # Interactive mode for custom prompts
    if args.interactive:
        print("=== INTERACTIVE PROMPT MODE ===")
        print("Enter your custom system prompt below.")
        print("Press Enter twice when finished, or Ctrl+C to cancel.")
        print("-" * 50)
        
        prompt_lines = []
        try:
            while True:
                line = input()
                if line == "" and prompt_lines:  # Empty line and we have content
                    break
                prompt_lines.append(line)
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(0)
        
        custom_prompt = '\n'.join(prompt_lines)
        if not custom_prompt.strip():
            print("No prompt entered. Exiting.")
            sys.exit(0)
        
        question = "Please analyze the uploaded file using the custom instructions provided."
        
    elif args.prompt:
        custom_prompt = args.prompt
        question = args.question or "Please analyze the uploaded file."
        
    elif args.question:
        custom_prompt = None
        question = args.question
        
    else:
        print("Error: Please provide either --question, --prompt, or use --interactive mode")
        print("\nExamples:")
        print("  python test.py --question 'How many complaints are from Israel?'")
        print("  python test.py --interactive")
        print("  python test.py --prompt 'You are an expert analyst...'")
        sys.exit(1)
    
    try:
        # Initialize analyzer
        analyzer = FileAnalyzer(api_key=args.api_key)
        
        # Upload file
        print(f"Uploading file: {args.file}")
        file_content = analyzer.upload_file(args.file)
        print(f"File uploaded successfully. Size: {len(file_content)} characters")
        
        # Show what we're doing
        if args.interactive:
            print(f"\nUsing interactive custom prompt")
        elif args.prompt:
            print(f"\nUsing custom prompt")
        else:
            print(f"\nAsking question: {question}")
        
        print("=" * 50)
        
        filename = os.path.basename(args.file)
        # Update the uploaded files reference for the API call
        response = analyzer.ask_question(f"The uploaded file is named '{filename}'. {question}", file_content, custom_prompt)
        
        print(response)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()