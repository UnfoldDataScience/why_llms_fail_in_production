import gradio as gr
from uncontrolled_system import UncontrolledSystem
from governed_system import GovernedSystem

uncontrolled = UncontrolledSystem()
governed = GovernedSystem()

def process_comparison(user_input, mode):
    if not user_input.strip():
        return "Please enter a refund request.", "", "", "", "", ""
    
    if mode == "Uncontrolled LLM Mode":
        result = uncontrolled.process_request(user_input)
        
        reasoning = result.get("reasoning", "N/A")
        action = result.get("action_taken", "N/A")
        explanation = result.get("explanation", "N/A")
        deterministic = "❌ UNSTABLE" if not result.get("deterministic", False) else "✅ STABLE"
        audit_log = result.get("audit_log", "N/A")
        
        return (
            reasoning,
            action,
            explanation,
            deterministic,
            audit_log,
            ""
        )
    
    elif mode == "Governed (EDCA) Mode":
        result = governed.process_request(user_input)
        
        reasoning = result.get("reasoning", "N/A")
        action = result.get("action_taken", "N/A")
        explanation = result.get("explanation", "N/A")
        deterministic = "✅ STABLE" if result.get("deterministic", False) else "❌ UNSTABLE"
        audit_log = result.get("audit_log", "N/A")
        
        return (
            reasoning,
            action,
            explanation,
            deterministic,
            audit_log,
            ""
        )
    
    else:
        uncontrolled_result = uncontrolled.process_request(user_input)
        governed_result = governed.process_request(user_input)
        
        uncontrolled_reasoning = uncontrolled_result.get("reasoning", "N/A")
        uncontrolled_action = uncontrolled_result.get("action_taken", "N/A")
        uncontrolled_explanation = uncontrolled_result.get("explanation", "N/A")
        uncontrolled_deterministic = "❌ UNSTABLE" if not uncontrolled_result.get("deterministic", False) else "✅ STABLE"
        uncontrolled_audit = uncontrolled_result.get("audit_log", "N/A")
        
        governed_reasoning = governed_result.get("reasoning", "N/A")
        governed_action = governed_result.get("action_taken", "N/A")
        governed_explanation = governed_result.get("explanation", "N/A")
        governed_deterministic = "✅ STABLE" if governed_result.get("deterministic", False) else "❌ UNSTABLE"
        governed_audit = governed_result.get("audit_log", "N/A")
        
        comparison = f"""
## Side-by-Side Comparison

### Uncontrolled System
- **Action**: {uncontrolled_action}
- **Determinism**: {uncontrolled_deterministic}
- **Explanation**: {uncontrolled_explanation}

### Governed System
- **Action**: {governed_action}
- **Determinism**: {governed_deterministic}
- **Explanation**: {governed_explanation}

### Key Differences
- Uncontrolled system executes actions directly based on LLM output
- Governed system validates and enforces rules before execution
- Same input may produce different results in uncontrolled mode
- Governed mode ensures consistent, auditable outcomes
"""
        
        return (
            f"**Uncontrolled:**\n{uncontrolled_reasoning}\n\n**Governed:**\n{governed_reasoning}",
            f"**Uncontrolled:** {uncontrolled_action}\n\n**Governed:** {governed_action}",
            comparison,
            f"**Uncontrolled:** {uncontrolled_deterministic}\n\n**Governed:** {governed_deterministic}",
            f"**Uncontrolled:**\n{uncontrolled_audit}\n\n**Governed:**\n{governed_audit}",
            ""
        )

def reset_systems():
    uncontrolled.reset_conversation()
    return "Systems reset. Conversation history cleared for uncontrolled system."

with gr.Blocks(title="Why LLM Systems Fail in Production") as app:
    gr.Markdown("""
    # Why LLM Systems Fail in Production (It's Not the Model)
    
    This demonstration shows how **system design**, not the LLM model, causes production failures.
    
    **Try the same refund request multiple times** to see inconsistent behavior in the uncontrolled system.
    """)
    
    with gr.Row():
        with gr.Column():
            mode = gr.Radio(
                choices=["Side-by-Side Comparison", "Uncontrolled LLM Mode", "Governed (EDCA) Mode"],
                value="Side-by-Side Comparison",
                label="System Mode"
            )
            
            user_input = gr.Textbox(
                label="Refund Request",
                placeholder="Example: Customer wants refund for order #12345, amount $250, reason: defective product received",
                lines=3
            )
            
            with gr.Row():
                submit_btn = gr.Button("Process Request", variant="primary")
                reset_btn = gr.Button("Reset Systems")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### LLM Reasoning")
            reasoning_output = gr.Textbox(label="", lines=8, interactive=False)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Action Taken")
            action_output = gr.Textbox(label="", lines=3, interactive=False)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### System Explanation")
            explanation_output = gr.Markdown(label="")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Determinism Status")
            deterministic_output = gr.Textbox(label="", lines=2, interactive=False)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Audit Log")
            audit_output = gr.Textbox(label="", lines=10, interactive=False)
    
    reset_status = gr.Textbox(label="", visible=False)
    
    submit_btn.click(
        fn=process_comparison,
        inputs=[user_input, mode],
        outputs=[reasoning_output, action_output, explanation_output, deterministic_output, audit_output, reset_status]
    )
    
    reset_btn.click(
        fn=reset_systems,
        outputs=[reset_status]
    )

if __name__ == "__main__":
    app.launch(server_name="127.0.0.1", server_port=7860, theme=gr.themes.Soft())

