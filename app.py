print(f"\n{clr.RED}Softener 1 Prolonged Zero Flow Events (>= {min_duration} minutes):{clr.END}")
if softener1_events:
    for event in softener1_events:
        print(f"  Start: {event['Start Time']}, End: {event['End Time']}, Duration: {event['Duration (minutes)']} minutes")
else:
    print(f"{clr.RED}  No prolonged zero flow events found for Softener 1.{clr.END}")

print(f"\n{clr.RED}Softener 2 Prolonged Zero Flow Events (>= {min_duration} minutes):{clr.END}")
if softener2_events:
    for event in softener2_events:
        print(f"  Start: {event['Start Time']}, End: {event['End Time']}, Duration: {event['Duration (minutes)']} minutes")
else:
    print(f"{clr.RED}  No prolonged zero flow events found for Softener 2.{clr.END}")

print(f"\n{clr.RED}Softener 3 Prolonged Zero Flow Events (>= {min_duration} minutes):{clr.END}")
if softener3_events:
    for event in softener3_events:
        print(f"  Start: {event['Start Time']}, End: {event['End Time']}, Duration: {event['Duration (minutes)']} minutes")
else:
    print(f"{clr.RED}  No prolonged zero flow events found for Softener 3.{clr.END}")

これも
