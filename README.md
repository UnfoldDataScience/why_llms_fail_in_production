# Why LLM Systems Fail in Production (It's Not the Model)

This project demonstrates a critical insight: **LLM system failures in production are typically caused by system design flaws, not the LLM model itself**.

## What This Project Demonstrates

This project implements two contrasting systems that process the same refund approval requests:

1. **System A: Uncontrolled LLM System** - LLM directly decides and executes actions
2. **System B: Governed LLM System (EDCA-style)** - LLM provides reasoning only, deterministic execution layer handles actions

## Why the Uncontrolled System Fails

The uncontrolled system exhibits classic production failure patterns:

- **No execution control**: LLM directly executes actions without validation
- **Non-deterministic behavior**: Same input can produce different outputs
- **Conversation history dependency**: Previous interactions unpredictably affect decisions
- **No audit trail**: Impossible to explain why decisions were made
- **Unclear failure modes**: When something goes wrong, the explanation is vague ("the model decided")

## Why the Governed System Works

The governed system implements EDCA-style (Execution-Decision-Control-Audit) architecture:

- **Separation of concerns**: LLM only reasons, execution engine validates and executes
- **Deterministic execution**: Rule-based validation ensures consistent outcomes
- **Structured outputs**: LLM must produce valid JSON that passes validation
- **Full audit trail**: Every decision, validation, and execution step is logged
- **Clear failure modes**: When validation fails, the reason is explicit and traceable

### How EDCA-Style Execution Control Works

1. **Reasoning Layer (LLM)**: Analyzes the request and provides structured reasoning in JSON format
2. **Validation Layer**: Checks if the proposed action and parameters meet business rules
3. **Execution Layer**: Performs the action only if validation passes
4. **Audit Layer**: Logs every step for traceability

The LLM never executes actions directly. It only provides structured reasoning that the execution engine validates against deterministic rules.

## Architecture

```
Uncontrolled System:
User Input → LLM → Direct Action Execution → Result

Governed System:
User Input → LLM (Reasoning) → Validation → Execution Engine → Result
                                    ↓
                              Audit Log
```



## Setup

### Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venvllm
   venvllm\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create `.env` file and put your OPENAI_API_KEY
   
5. Add your OpenAI API key to `.env`:
   ```
   OPENAI_API_KEY=your_key_here
   ```
6. Run the application:
   ```bash
   python main.py
   ```
7. Open your browser to `http://localhost:7860`


## Usage

1. Select a mode:
   - **Side-by-Side Comparison**: Run both systems on the same input
   - **Uncontrolled LLM Mode**: Test the uncontrolled system
   - **Governed (EDCA) Mode**: Test the governed system

2. Enter a refund request, for example:
   - "Customer wants refund for order #12345, amount $250, reason: defective product"
   - "Customer wants refund for order #67890, amount $1500, reason: wrong item"

3. Click "Process Request"

4. **Key test**: Run the same request multiple times in uncontrolled mode to see inconsistent behavior

## Example Scenarios

### Scenario 1: Standard Refund
**Input**: "Customer wants refund for order #12345, amount $250, reason: defective product"

- **Uncontrolled**: May approve, reject, or escalate depending on conversation history
- **Governed**: Always validates amount < $1000, reason in allowed list, then approves deterministically

### Scenario 2: High Amount
**Input**: "Customer wants refund for order #67890, amount $1500, reason: wrong item"

- **Uncontrolled**: May approve (ignoring policy) or reject inconsistently
- **Governed**: Rejects with clear message: "Amount 1500 exceeds maximum 1000" (validation rule enforced)

### Scenario 3: Invalid Reason
**Input**: "Customer wants refund for order #11111, amount $100, reason: changed mind"

- **Uncontrolled**: May approve or reject unpredictably
- **Governed**: Rejects with message: "Reason 'changed mind' not in allowed reasons" (policy enforced)
