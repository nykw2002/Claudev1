#!/usr/bin/env python3
"""
Smart Context Management OpenAI File Analyzer - test2.py

This version implements intelligent context management to handle token limits while
maintaining conversation continuity for tool calling sessions.

Key Features:
- Automatic conversation summarization when approaching token limits
- Independent session management for different analysis phases
- Preserves tool results and key findings while reducing token overhead
- Maintains analysis quality with smart context trimming

Requirements:
- openai>=1.0.0
- tiktoken (for token counting)
- python-dotenv (optional)

Usage:
    python test2.py --file test.txt --question "Analyze complaints categorization"
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

try:
    from openai import OpenAI
    import tiktoken
except ImportError:
    print("Error: Required packages not installed. Run: pip install openai tiktoken")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


# Configuration
DEFAULT_FILE = "test.txt"
DEFAULT_API_KEY = ""

# Token management settings
TOKEN_LIMIT = 25000  # Conservative limit for gpt-4o (30k actual limit)
MAX_RESPONSE_TOKENS = 2000
SUMMARY_TRIGGER_THRESHOLD = 12000  # Start summarizing earlier to support 25 iterations


class SmartContextFileAnalyzer:
    """File analyzer with intelligent context management for long conversations."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """Initialize with OpenAI API key and model selection."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set or not provided")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.working_dir = tempfile.mkdtemp(prefix='smart_context_analyzer_')
        self.uploaded_files = {}
        
        # Initialize token encoder
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")  # Default encoding
        
        # Analysis state tracking
        self.analysis_state = {
            "discoveries": [],
            "findings": [],
            "tool_results": [],
            "key_insights": []
        }
        
        print(f"✅ Initialized with model: {self.model}")
        print(f"🧠 Token limit: {TOKEN_LIMIT}, Summary threshold: {SUMMARY_TRIGGER_THRESHOLD}")
        
    def __del__(self):
        """Clean up temporary directory."""
        if hasattr(self, 'working_dir') and os.path.exists(self.working_dir):
            shutil.rmtree(self.working_dir)
    
    def count_tokens(self, messages: List[Dict]) -> int:
        """Count tokens in a message list."""
        try:
            total_tokens = 0
            for message in messages:
                # Count tokens for role
                total_tokens += 4  # Role overhead
                
                # Count content tokens
                if isinstance(message.get('content'), str):
                    total_tokens += len(self.encoding.encode(message['content']))
                elif isinstance(message.get('content'), list):
                    # Handle tool results and complex content
                    total_tokens += len(self.encoding.encode(json.dumps(message['content'])))
                
                # Count tool call tokens
                if 'tool_calls' in message:
                    for tool_call in message['tool_calls']:
                        total_tokens += len(self.encoding.encode(json.dumps(tool_call)))
            
            return total_tokens
        except Exception as e:
            print(f"⚠️ Token counting error: {e}")
            return len(str(messages)) // 3  # Rough estimate fallback
    
    def upload_file(self, file_path: str) -> str:
        """Upload a file to the working directory and return its content."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        filename = os.path.basename(file_path)
        dest_path = os.path.join(self.working_dir, filename)
        shutil.copy2(file_path, dest_path)
        
        try:
            with open(dest_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(dest_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        self.uploaded_files[filename] = {
            'path': dest_path,
            'content': content,
            'size': len(content)
        }
        
        return content
    
    def create_conversation_summary(self, messages: List[Dict]) -> str:
        """Create a concise summary of the conversation to preserve context."""
        # Extract key information from messages
        discoveries = []
        tool_results = []
        findings = []
        
        for msg in messages:
            if msg.get('role') == 'assistant' and msg.get('content'):
                content = msg['content']
                if 'found' in content.lower() or 'discovered' in content.lower():
                    findings.append(content[:200])
            
            if msg.get('role') == 'tool':
                try:
                    tool_data = json.loads(msg['content'])
                    if isinstance(tool_data, dict) and 'count' in tool_data:
                        tool_results.append(f"Count: {tool_data['count']}")
                    elif isinstance(tool_data, dict) and 'matches' in tool_data:
                        tool_results.append(f"Matches: {len(tool_data['matches'])}")
                except:
                    tool_results.append("Tool execution completed")
        
        summary_parts = []
        if findings:
            summary_parts.append(f"Key discoveries: {'; '.join(findings[:3])}")
        if tool_results:
            summary_parts.append(f"Tool results: {'; '.join(tool_results[:5])}")
        
        # Update analysis state
        self.analysis_state["findings"].extend(findings)
        self.analysis_state["tool_results"].extend(tool_results)
        
        return "; ".join(summary_parts) if summary_parts else "Analysis in progress"
    
    def trim_conversation_with_summary(self, messages: List[Dict]) -> List[Dict]:
        """Trim conversation intelligently while preserving key context."""
        print(f"🔄 Trimming conversation - current length: {len(messages)} messages")
        
        # Always preserve system message
        system_message = None
        conversation_messages = []
        
        for msg in messages:
            if msg.get('role') == 'system':
                system_message = msg
            else:
                conversation_messages.append(msg)
        
        # If we have too many messages, summarize the middle portion
        if len(conversation_messages) > 10:
            # Keep first 3 and last 5 messages, summarize the middle
            start_messages = conversation_messages[:3]
            end_messages = conversation_messages[-5:]
            middle_messages = conversation_messages[3:-5]
            
            if middle_messages:
                # Create summary of middle portion
                summary_text = self.create_conversation_summary(middle_messages)
                summary_message = {
                    "role": "assistant",
                    "content": f"[CONTEXT SUMMARY] Previous analysis revealed: {summary_text}"
                }
                
                trimmed_messages = start_messages + [summary_message] + end_messages
            else:
                trimmed_messages = start_messages + end_messages
        else:
            # If not too many messages, just keep recent ones
            trimmed_messages = conversation_messages[-8:]
        
        # Reconstruct with system message
        result = []
        if system_message:
            result.append(system_message)
        result.extend(trimmed_messages)
        
        print(f"✅ Trimmed to {len(result)} messages")
        return result
    
    def define_tools(self) -> List[Dict[str, Any]]:
        """Define comprehensive tools for document analysis."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "view_file",
                    "description": "Examine file structure and content to understand document layout.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string", "description": "Name of the file to view"},
                            "line_range": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Optional [start, end] to view specific lines"
                            }
                        },
                        "required": ["filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_text",
                    "description": "Search for text patterns. Try multiple variations if first attempt fails.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string", "description": "Name of the file to search"},
                            "pattern": {"type": "string", "description": "Search pattern"},
                            "case_sensitive": {"type": "boolean", "default": False},
                            "count_only": {"type": "boolean", "default": False}
                        },
                        "required": ["filename", "pattern"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "find_sections",
                    "description": "Locate document sections to understand structure and categorization.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string", "description": "Name of the file"},
                            "markers": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Section markers to find"
                            }
                        },
                        "required": ["filename"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_positions",
                    "description": "Determine categorization based on document position and structure.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "filename": {"type": "string", "description": "Name of the file"},
                            "items": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Items to analyze positions for"
                            },
                            "reference_lines": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Reference line numbers for section boundaries"
                            }
                        },
                        "required": ["filename", "items"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "run_command",
                    "description": "Execute shell commands for verification and cross-checking.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "Safe shell command to execute"},
                            "filename": {"type": "string", "description": "File to operate on (optional)"}
                        },
                        "required": ["command"]
                    }
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
            elif tool_name == "find_document_sections":
                return self._find_document_sections(tool_input)
            elif tool_name == "extract_line_ranges":
                return self._extract_line_ranges(tool_input)
            elif tool_name == "analyze_line_positions":
                return self._analyze_line_positions(tool_input)
            elif tool_name == "run_command":
                return self._run_command(tool_input)
            elif tool_name == "analyze_data":
                return self._analyze_data(tool_input)
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def _view_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """View file contents with optional line range."""
        filename = args.get("filename")
        line_range = args.get("line_range")
        
        if filename not in self.uploaded_files:
            return {"error": f"File not found: {filename}"}
        
        content = self.uploaded_files[filename]["content"]
        lines = content.split('\n')
        
        if line_range and len(line_range) == 2:
            start, end = line_range
            start = max(1, start) - 1  # Convert to 0-based indexing
            end = min(len(lines), end)
            selected_lines = lines[start:end]
            numbered_content = '\n'.join([f"{i+start+1:5d}\t{line}" for i, line in enumerate(selected_lines)])
        else:
            # Show first 100 lines with line numbers for structure understanding
            display_lines = lines[:100]
            numbered_content = '\n'.join([f"{i+1:5d}\t{line}" for i, line in enumerate(display_lines)])
            if len(lines) > 100:
                numbered_content += f"\n... ({len(lines) - 100} more lines)"
        
        return {
            "content": numbered_content,
            "total_lines": len(lines),
            "file_size": len(content),
            "structure_info": f"Document has {len(lines)} lines total"
        }
    
    def _search_text(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search for text patterns in files with detailed results."""
        filename = args.get("filename")
        pattern = args.get("pattern")
        case_sensitive = args.get("case_sensitive", False)
        count_only = args.get("count_only", False)
        
        if filename not in self.uploaded_files:
            return {"error": f"File not found: {filename}"}
        
        content = self.uploaded_files[filename]["content"]
        
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            matches = list(re.finditer(pattern, content, flags))
            
            if count_only:
                return {"count": len(matches), "pattern": pattern}
            
            # Return detailed match information with line context
            results = []
            lines = content.split('\n')
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                
                results.append({
                    "match": match.group(),
                    "line_number": line_num,
                    "line_content": line_content.strip(),
                    "start_position": match.start(),
                    "end_position": match.end()
                })
            
            return {
                "matches": results,
                "count": len(matches),
                "pattern": pattern,
                "suggestion": f"Found {len(matches)} matches. If this seems low, try variations like '{pattern.lower()}', '{pattern.upper()}' or broader patterns."
            }
            
        except re.error as e:
            return {"error": f"Invalid regex pattern: {str(e)}"}
    
    def _find_document_sections(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Find and analyze document sections to understand structure."""
        filename = args.get("filename")
        section_markers = args.get("section_markers", ["substantiated", "unsubstantiated", "complaints", "section", "table"])
        
        if filename not in self.uploaded_files:
            return {"error": f"File not found: {filename}"}
        
        content = self.uploaded_files[filename]["content"]
        lines = content.split('\n')
        
        sections_found = {}
        
        for marker in section_markers:
            pattern = rf'\b{re.escape(marker)}\b'
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            
            section_info = []
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                
                # Get context around the section marker
                context_start = max(0, line_num - 3)
                context_end = min(len(lines), line_num + 3)
                context_lines = []
                for i in range(context_start, context_end):
                    context_lines.append(f"{i+1:5d}: {lines[i]}")
                
                section_info.append({
                    "line_number": line_num,
                    "line_content": line_content.strip(),
                    "context": "\n".join(context_lines)
                })
            
            if section_info:
                sections_found[marker] = {
                    "count": len(section_info),
                    "locations": section_info
                }
        
        return {
            "sections_found": sections_found,
            "total_lines": len(lines),
            "analysis": "Found document sections. Use these to understand how content is organized and categorized."
        }
    
    def _extract_line_ranges(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract line ranges around specific line numbers for context analysis."""
        filename = args.get("filename")
        line_numbers = args.get("line_numbers", [])
        context_lines = args.get("context_lines", 10)
        
        if filename not in self.uploaded_files:
            return {"error": f"File not found: {filename}"}
        
        content = self.uploaded_files[filename]["content"]
        lines = content.split('\n')
        
        extracted_ranges = {}
        
        for line_num in line_numbers:
            if 1 <= line_num <= len(lines):
                start_line = max(1, line_num - context_lines)
                end_line = min(len(lines), line_num + context_lines)
                
                context_lines_data = []
                for i in range(start_line - 1, end_line):  # Convert to 0-based indexing
                    context_lines_data.append({
                        "line_number": i + 1,
                        "content": lines[i],
                        "is_target": (i + 1) == line_num
                    })
                
                extracted_ranges[line_num] = {
                    "context_start": start_line,
                    "context_end": end_line,
                    "lines": context_lines_data
                }
            else:
                extracted_ranges[line_num] = {"error": f"Line number {line_num} out of range"}
        
        return {
            "extracted_ranges": extracted_ranges,
            "total_ranges": len(extracted_ranges)
        }
    
    def _analyze_line_positions(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze where items appear in document to determine categorization."""
        filename = args.get("filename")
        search_items = args.get("search_items", [])
        section_boundaries = args.get("section_boundaries", {})
        
        if filename not in self.uploaded_files:
            return {"error": f"File not found: {filename}"}
        
        content = self.uploaded_files[filename]["content"]
        lines = content.split('\n')
        
        position_analysis = {}
        
        for item in search_items:
            item_positions = []
            pattern = re.escape(str(item))
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                
                # Determine section based on line number and boundaries
                section = self._determine_section_by_position(line_num, section_boundaries, len(lines))
                
                item_positions.append({
                    "line_number": line_num,
                    "line_content": line_content.strip(),
                    "determined_section": section,
                    "position_in_file": match.start()
                })
            
            position_analysis[item] = {
                "positions": item_positions,
                "count": len(item_positions)
            }
        
        return {
            "position_analysis": position_analysis,
            "analysis_summary": f"Analyzed positions of {len(search_items)} items to determine categorization"
        }
    
    def _determine_section_by_position(self, line_num: int, section_boundaries: Dict, total_lines: int) -> str:
        """Determine which section a line number falls into."""
        if section_boundaries:
            for section_name, boundaries in section_boundaries.items():
                if isinstance(boundaries, dict) and 'start' in boundaries and 'end' in boundaries:
                    if boundaries['start'] <= line_num <= boundaries['end']:
                        return section_name
        
        # Default categorization based on position
        if line_num < total_lines * 0.3:
            return "document_header_or_substantiated"
        elif line_num < total_lines * 0.7:
            return "middle_section"
        else:
            return "unsubstantiated_or_appendix"
    
    def _run_command(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute shell commands safely for advanced analysis."""
        command = args.get("command", "")
        filename = args.get("filename")

        # Security check: only allow safe commands
        safe_commands = ['grep', 'wc', 'head', 'tail', 'cat', 'awk', 'sed', 'sort', 'uniq', 'cut', 'find', 'findstr']
        if not any(command.strip().startswith(cmd) for cmd in safe_commands):
            return {"error": f"Command not allowed: {command}"}

        try:
            # If filename specified, update command to use full path
            if filename and filename in self.uploaded_files:
                file_path = self.uploaded_files[filename]["path"]

                # Handle grep commands specially for cross-platform compatibility
                if command.strip().startswith('grep'):
                    # On Windows, use Python-based grep instead
                    if sys.platform == 'win32':
                        pattern = command.split("'")[1] if "'" in command else command.split()[1]
                        content = self.uploaded_files[filename]["content"]

                        # Count matches
                        import re
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        count = len(matches)

                        return {
                            "stdout": f"{count}\n",
                            "stderr": "",
                            "return_code": 0,
                            "command": f"Python grep simulation for: {command}",
                            "note": "Using Python regex instead of grep (Windows compatibility)"
                        }

                command = command.replace(filename, file_path)

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.working_dir,
                timeout=30
            )

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": command
            }

        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}
        except Exception as e:
            return {"error": f"Command execution failed: {str(e)}"}
    
    def ask_question(self, question: str, file_content: str = None, custom_prompt: str = None) -> str:
        """Ask a question using enhanced persistent analysis approach."""
        
        # Enhanced system message for thorough, persistent analysis
        if custom_prompt:
            system_content = custom_prompt
        else:
            system_content = """You are a thorough document analysis expert. For complex analysis tasks, use 15-25 tool iterations to build complete understanding.

SYSTEMATIC APPROACH:
1. Start with file structure examination (view_file) 
2. Find document sections and understand organization (find_document_sections)
3. Search for entities using multiple patterns if needed (search_text with variations)
4. Analyze positions and context (extract_line_ranges, analyze_line_positions) 
5. Cross-reference between sections to determine categorization
6. Verify with shell commands (run_command with grep/wc)
7. Provide comprehensive final analysis

PERSISTENCE: If a search fails, try variations:
- Different cases (Israel vs israel vs ISRAEL)
- Abbreviations (South Korea vs Korea vs KR)  
- Broader patterns, then narrow down
- Use context to understand document structure

Never give up after just a few attempts. Complex analysis requires thorough exploration."""
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": question}
        ]
        
        print(f"🧠 Using {self.model} with enhanced persistent analysis")
        print(f"💭 Question: {question}")
        
        try:
            max_iterations = 25  # Increased for thorough analysis
            iteration = 0

            while iteration < max_iterations:
                iteration += 1
                print(f"\n🔄 Iteration {iteration}")

                # Check token count and trim if needed
                current_tokens = self.count_tokens(messages)
                print(f"📊 Current tokens: {current_tokens}/{TOKEN_LIMIT}")

                if current_tokens > SUMMARY_TRIGGER_THRESHOLD:
                    print(f"⚠️ Token threshold reached ({current_tokens} > {SUMMARY_TRIGGER_THRESHOLD})")
                    print(f"🔄 Trimming conversation to reduce tokens...")
                    messages = self.trim_conversation_with_summary(messages)
                    new_token_count = self.count_tokens(messages)
                    print(f"✅ Reduced tokens from {current_tokens} to {new_token_count}")

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.define_tools(),
                    tool_choice="auto",
                    max_tokens=2000  # Reduced to avoid rate limits
                )

                if response.choices[0].finish_reason == "tool_calls":
                    tool_calls = response.choices[0].message.tool_calls
                    print(f"🔧 Executing {len(tool_calls)} tool(s)")

                    # Add assistant's response
                    messages.append({
                        "role": "assistant",
                        "content": response.choices[0].message.content,
                        "tool_calls": tool_calls
                    })

                    # Process tool calls
                    for tool_call in tool_calls:
                        tool_name = tool_call.function.name
                        print(f"🛠️ Tool: {tool_name}")

                        try:
                            args = json.loads(tool_call.function.arguments)
                            result = self.execute_tool(tool_name, args)

                            # Show abbreviated result for readability
                            result_str = str(result)
                            if len(result_str) > 200:
                                result_preview = result_str[:200] + "..."
                            else:
                                result_preview = result_str
                            print(f"✅ Result: {result_preview}")

                            # Truncate large results to save tokens
                            if len(json.dumps(result)) > 3000:
                                if isinstance(result, dict) and 'matches' in result:
                                    # Keep only essential match info
                                    truncated_result = {
                                        'count': result.get('count', 0),
                                        'pattern': result.get('pattern', ''),
                                        'matches': result['matches'][:5],  # Keep first 5
                                        'truncated': True,
                                        'original_count': len(result['matches'])
                                    }
                                    result = truncated_result

                            messages.append({
                                "role": "tool",
                                "content": json.dumps(result),
                                "tool_call_id": tool_call.id
                            })
                        except Exception as e:
                            print(f"❌ Tool execution failed: {e}")
                            messages.append({
                                "role": "tool",
                                "content": json.dumps({"error": str(e)}),
                                "tool_call_id": tool_call.id
                            })
                else:
                    # Model provided final response
                    print(f"🎯 Analysis complete after {iteration} iterations")
                    return response.choices[0].message.content
            
            # If we hit max iterations, ask for summary
            print(f"⚠️ Reached maximum iterations ({max_iterations}), generating summary")
            messages.append({
                "role": "user", 
                "content": "Please provide a comprehensive summary based on all the analysis performed so far."
            })
            
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000
            )
            
            return final_response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return f"Analysis encountered an error: {str(e)}"


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Smart Context Management OpenAI file analyzer - test2.py")
    parser.add_argument("--file", default=DEFAULT_FILE, help=f"Path to the file to analyze (default: {DEFAULT_FILE})")
    parser.add_argument("--question", help="Question to ask about the file")
    parser.add_argument("--prompt", help="Custom system prompt")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode for custom prompts")
    parser.add_argument("--api-key", default=DEFAULT_API_KEY, help="OpenAI API key")
    parser.add_argument("--model", default="gpt-4o", choices=["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"], help="Model to use")
    
    args = parser.parse_args()
    
    # Handle interactive mode
    if args.interactive:
        print("=== INTERACTIVE PROMPT MODE ===")
        print("Enter your custom system prompt below.")
        print("Press Enter twice when finished, or Ctrl+C to cancel.")
        print("-" * 50)
        
        prompt_lines = []
        try:
            while True:
                line = input()
                if line == "" and prompt_lines:
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
        print("  python test2.py --question 'Count complaints from Israel and South Korea, categorize them'")
        print("  python test2.py --interactive")
        sys.exit(1)
    
    try:
        print(f"🚀 Smart Context Management OpenAI File Analyzer - test2.py")
        print(f"📋 Model: {args.model}")
        
        # Initialize analyzer
        analyzer = SmartContextFileAnalyzer(api_key=args.api_key, model=args.model)
        
        # Upload file
        print(f"\n📁 Uploading file: {args.file}")
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
            
        file_content = analyzer.upload_file(args.file)
        print(f"✅ File uploaded successfully")
        print(f"📊 File size: {len(file_content)} characters")
        
        # Prepare final question
        filename = os.path.basename(args.file)
        final_question = f"The uploaded file is named '{filename}'. {question}"
        
        print("\n" + "=" * 60)
        print("🔍 STARTING SMART CONTEXT ANALYSIS")
        print("=" * 60)
        
        # Analyze file
        response = analyzer.ask_question(final_question, file_content, custom_prompt)
        
        print("\n" + "=" * 60)
        print("📋 ANALYSIS RESULTS")
        print("=" * 60)
        print(response)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(f"❌ Traceback:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()