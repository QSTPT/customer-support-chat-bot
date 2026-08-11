import json

JSON_EXAMPLES: list[dict[str, str]] = [
    {
        "role": "user",
        "content": "My VPN keeps disconnecting every few minutes.",
    },
    {
        "role": "assistant",
        "content": json.dumps({
            "in_scope": True,
            "category": "connection",
            "answer": "Frequent drops usually come from protocol or "
                "power settings. Work through these, then tell "
                "me your OS and protocol if it persists.",
            
            "steps": [
                "Switch protocol to WireGuard in Settings > Protocol.",
                "Try a server in a closer region.",
                "Disable battery optimization for the app.",
            ],
            "escalate": False,
        })
    },
    {
        "role": "user",
        "content": "Who won the World Cup in 2022?",
    },
    {
        "role": "assistant",
        "content": json.dumps({
            "in_scope": False,
            "category": "other",
            "answer": "I can only help with VPN-related questions. Is "
                "there something about your VPN service I can "
                "assist with?",
            "steps": [],
            "escalate": False,
        }),
    },
    {
        "role": "user",
        "content": "Does the kill switch work on mobile?",
    },
    {
        "role": "assistant",
        "content":  json.dumps({
            "in_scope": True,
            "category": "privacy",
            "answer": "Yes. The kill switch blocks all traffic if the "
                "tunnel drops, and it's available on both iOS "
                "and Android under Settings > Connection. It "
                "stays active until you disconnect manually.",
            "steps": [],
            "escalate": False,
            }),
    },
]

PROSE_EXAMPLES: list[dict[str, str]] = [
    {
        "role": "user",
        "content": "My VPN keeps disconnecting every few minutes.",
    },
    {
        "role": "assistant",
        "content": (
            "Frequent drops usually come from protocol or power "
            "settings. Try these:\n"
            "1. Switch protocol to WireGuard in Settings > Protocol.\n"
            "2. Try a server in a closer region.\n"
            "3. Disable battery optimization for the app.\n"
            "If it persists, tell me your OS and protocol."
        ),
    },
    {
        "role": "user",
        "content": "Who won the World Cup in 2022?",
    },
    {
        "role": "assistant",
        "content": (
            "I can only help with VPN-related questions. Is there "
            "something about your VPN service I can assist with?"
        ),
    },
    {
        "role": "user",
        "content": "Does the kill switch work on mobile?",
    },
    {
        "role": "assistant",
        "content": (
            "Yes. The kill switch blocks all traffic if the tunnel "
            "drops, and it's available on both iOS and Android under "
            "Settings > Connection. It stays active until you "
            "disconnect manually."
        ),
    },
]


EXAMPLES = {
    "default": PROSE_EXAMPLES,
    "structured": JSON_EXAMPLES,
}

def build_messages(
    preset: str,
    user_prompt: str,
    schema_json: str = "",
) -> list[dict[str, str]]:
    system = PROMPTS[preset].replace("{{SCHEMA}}", schema_json)
    return [
        {"role": "system", "content": system},
        *EXAMPLES.get(preset, []),
        {"role": "user", "content": user_prompt},
    ]