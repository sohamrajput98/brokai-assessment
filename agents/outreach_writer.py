import os
from agents.llm_client import call_llm_quality


class OutreachWriterAgent:
    """
    Agent 03 - Outreach Writer
    Input: profile, contact card, company name
    Output: WhatsApp-style cold outreach message string
    """

    def __init__(self):
            pass

    def run(self, profile: dict, contact: dict, company_name: str) -> str:
        summary = profile.get("summary", "a business in Rajasthan")
        digital = profile.get("digital_presence", "")
        uses_crm = profile.get("uses_crm_or_booking", "Unknown")

        if uses_crm in ("No", "Unknown"):
            angle = "They likely handle customer calls and follow-ups manually."
        else:
            angle = "They have some systems in place but may benefit from automation."

        prompt = f"""Write a cold WhatsApp outreach message on behalf of Brokai Labs.

Brokai Labs builds AI systems for small and medium businesses — voice receptionists, field operations dashboards, and communication automation. We help SMBs cut manual work and respond to leads faster.

Prospect:
- Company: {company_name}
- What they do: {summary}
- Digital presence: {digital}
- Uses CRM/booking: {uses_crm}
- Context: {angle}

Write a message that:
1. Is 4-5 lines max
2. Opens with something specific to their business, not a generic opener
3. Mentions one concrete outcome relevant to a solar EPC company
4. Ends with a soft CTA — ask if open to a quick chat, not a hard sell
5. Sounds like a human wrote it, not a bot
6. No emojis, no subject line, no sign-off like "Best regards"

Return only the message body, nothing else."""

        try:
            return call_llm_quality(prompt, max_tokens=300, temperature=0.7)
        
        except Exception as e:
            return f"Message generation failed: {e}"