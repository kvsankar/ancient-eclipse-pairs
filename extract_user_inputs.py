#!/usr/bin/env python3
"""
Extract only user inputs from Claude conversation markdown files.
"""

import re
import sys

def extract_user_messages(filepath):
    """Extract all user messages from a conversation markdown file."""

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by message sections
    messages = re.split(r'^## Message \d+ - ', content, flags=re.MULTILINE)

    user_messages = []

    for i, message in enumerate(messages):
        # Check if this is a user message
        if message.startswith('👤 User'):
            # Extract the timestamp
            timestamp_match = re.search(r'\*(\d{4}-\d{2}-\d{2}T[\d:\.]+Z)\*', message)
            timestamp = timestamp_match.group(1) if timestamp_match else 'Unknown'

            # Extract content between timestamp and metadata section
            # The content is after the timestamp and before "### Metadata"
            content_match = re.search(r'\*\d{4}-\d{2}-\d{2}T[\d:\.]+Z\*\n\n(.*?)\n### Metadata',
                                     message, re.DOTALL)

            if content_match:
                user_content = content_match.group(1).strip()

                # Skip tool results - only keep actual human inputs
                if not user_content.startswith('**[Tool Result'):
                    user_messages.append({
                        'timestamp': timestamp,
                        'content': user_content,
                        'number': len(user_messages) + 1
                    })

    return user_messages

def main():
    filepath = 'claude-conversations/eclipse-challenge/20251122113415_947ad35a-92ef-4b0b-b473-b7c11be44068.md'

    user_messages = extract_user_messages(filepath)

    # Write to output file
    output = []
    output.append("# Human Inputs from Eclipse Challenge Conversation\n")
    output.append(f"**Total User Messages:** {len(user_messages)}\n")
    output.append(f"**First Message:** {user_messages[0]['timestamp'] if user_messages else 'N/A'}\n")
    output.append(f"**Last Message:** {user_messages[-1]['timestamp'] if user_messages else 'N/A'}\n")
    output.append("\n---\n\n")

    for msg in user_messages:
        output.append(f"## Input {msg['number']}\n")
        output.append(f"*{msg['timestamp']}*\n\n")
        output.append(f"{msg['content']}\n\n")
        output.append("---\n\n")

    # Write to file
    output_file = 'human_inputs.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(output))

    print(f"✓ Extracted {len(user_messages)} user messages")
    print(f"✓ Saved to {output_file}")

if __name__ == '__main__':
    main()
