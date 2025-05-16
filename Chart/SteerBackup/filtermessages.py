# Load and filter CAN dump log
def extract_unique_can_messages(file_path, target_can_id="000000C4"):
    unique_messages = []
    seen_payloads = set()

    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            print(parts)
            if len(parts) >= 5 and parts[1] == target_can_id:
                # Reconstruct the 8-byte data payload as a string
                data = ' '.join(parts[3:])
                if data not in seen_payloads:
                    seen_payloads.add(data)
                    unique_messages.append((parts[1], data))
    
    return unique_messages

# Example usage
file_path = "logfile.txt"  # replace with your actual path
unique_c4_messages = extract_unique_can_messages(file_path)

# Optional: print or convert to DataFrame
for can_id, data in unique_c4_messages:
    print(f"{can_id}: {data}")

print(f"Total unique messages: {len(unique_c4_messages)}")