

# FactoryGuard AI



### Offline AI-Assisted Industrial Fault Diagnosis with Deterministic Safety Enforcement



FactoryGuard AI combines offline AI-assisted industrial fault diagnosis with deterministic safety enforcement and operator-controlled simulated recovery.



Built for the \*\*GDG Windsor Build with AI — Smart Automation, Robotics, and Vision Hackathon (November 2026)\*\*.



## 1. The Industrial Problem



Industrial equipment can experience conveyor jams, overheating, abnormal vibration, and electrical overloads.



Traditional threshold-based monitoring can detect unsafe sensor values but may provide limited diagnostic context. AI systems can assist with interpreting observations and maintenance documents, but their outputs must not independently authorize equipment restart.



FactoryGuard AI demonstrates an architecture that separates AI-generated maintenance advice from deterministic machine safety decisions.



## 2. Key Innovation



FactoryGuard AI combines:



\- Deterministic sensor monitoring and fault detection

\- A locally executed vision-language model

\- Retrieval-augmented maintenance guidance

\- LangGraph-based diagnostic orchestration

\- Behavior-tree-based simulated recovery

\- Operator acknowledgement and explicit approval

\- Fault-episode-bound recovery authorization

\- Persistent diagnostic and audit records

\- An interactive Streamlit dashboard



\*\*Core safety principle: AI provides advisory information; deterministic controls enforce machine safety.\*\*



## 3. System Architecture



```mermaid

flowchart TD

&#x20;   A\[Simulated Industrial Machine] --> B\[Sensor Readings and Scenario Images]

&#x20;   B --> C\[Deterministic Safety Controller]

&#x20;   B --> D\[LangGraph Diagnostic Workflow]



&#x20;   D --> E\[Local Gemma 3 Vision Analysis]

&#x20;   D --> F\[Maintenance Document Retrieval]

&#x20;   F --> G\[Local Gemma 3 Maintenance Advisor]

&#x20;   E --> H\[Diagnostic Agent]

&#x20;   G --> H

&#x20;   C --> H



&#x20;   H --> I\[Structured Diagnostic Report]

&#x20;   I --> J\[Streamlit Dashboard and Audit History]

&#x20;   I --> K\[Operator Review]



&#x20;   C --> L\[Deterministic Recovery Checks]

&#x20;   K --> L

&#x20;   L --> M\[Behavior-Tree Simulated Recovery]

&#x20;   M --> N\[Simulated Machine State]

```



The safety controller remains independent of model-generated recommendations.



### Diagnostic workflow



The LangGraph pipeline follows these stages:



1\. Validate input and sensor context.

2\. Inspect the simulated scene using the local vision-language model.

3\. Retrieve relevant maintenance documentation.

4\. Generate grounded maintenance advice when supporting documents are available.

5\. Combine evidence into a structured diagnostic report.

6\. Prepare the operator handoff.



Invalid input and unavailable AI components are handled without granting restart authorization.



## 4. Technology Stack



| Component | Technology |

| --- | --- |

| Programming language | Python 3.12 |

| Dashboard | Streamlit |

| Diagnostic orchestration | LangGraph |

| Local vision-language model | Gemma 3 4B through Ollama |

| Local embeddings | nomic-embed-text through Ollama |

| Maintenance retrieval | Local document retrieval and embeddings |

| Recovery orchestration | py\_trees |

| Deterministic safety | Python safety controller and interlocks |

| Persistent records | SQLite |

| Evaluation | pytest and Python evaluation scripts |

| Visualizations | Plotly and Matplotlib |



The prototype is designed to operate locally without cloud-based inference.



## 5. Repository Structure



```text

factoryguard-ai/

├── app/

│   └── dashboard.py

├── src/

│   ├── simulator/

│   ├── safety/

│   ├── vision/

│   ├── agents/

│   ├── rag/

│   ├── recovery/

│   └── storage/

├── data/

│   ├── scenarios/

│   └── manuals/

├── tests/

├── evaluation/

├── docs/

├── day6\_diagnostic\_demo.py

├── day7\_demo.py

├── day10\_demo.py

├── requirements.txt

└── README.md

```



## 6. Installation Requirements



Recommended development environment:



\- Windows 10 or Windows 11

\- Python 3.12

\- Git

\- Ollama installed locally

\- Sufficient RAM and disk space for local Gemma 3 inference



The prototype was developed and tested on a laptop with 16 GB RAM, an Intel Core i7 processor, and integrated graphics.



Inference performance depends on hardware.



### Clone the repository



```cmd

git clone <PUBLIC\_GITHUB\_REPOSITORY\_URL>

cd factoryguard-ai

```



Replace the repository URL with the published GitHub URL.



### Create a Python virtual environment



```cmd

py -3.12 -m venv .venv

.venv\\Scripts\\activate.bat

```



### Install dependencies



```cmd

python -m pip install -r requirements.txt

```



## 7. Configure Local Ollama Models



Install Ollama from:



https://ollama.com/



Download the required models:



```cmd

ollama pull gemma3:4b

ollama pull nomic-embed-text

```



Verify installed models:



```cmd

ollama list

```



Ensure the Ollama service is running locally at:



```text

http://localhost:11434

```



Model downloads require internet access. Once the models and dependencies are installed, the demonstrated diagnostic workflow can run without an internet connection.



## 8. Launch the Dashboard



From the project root, with the virtual environment activated and Ollama running:



```cmd

python -m streamlit run app/dashboard.py

```



Open the local dashboard, normally available at:



http://localhost:8501



The dashboard supports simulated machine monitoring, fault injection, AI-assisted diagnostics, recovery-state inspection, and diagnostic history.



## 9. Reproduce Industrial Scenarios



Four predefined simulated machine scenarios are available:



| Scenario | Temperature | Current | Vibration | RPM | Expected safety state |

| --- | ---: | ---: | ---: | ---: | --- |

| Normal | 55 °C | 8 A | 2.1 mm/s | 1450 | RUNNING |

| Conveyor jam | 72 °C | 19 A | 5.0 mm/s | 200 | STOPPED\_FAULT |

| Overheating | 96 °C | 10 A | 3.0 mm/s | 1400 | STOPPED\_FAULT |

| High vibration | 65 °C | 9 A | 9.2 mm/s | 1350 | STOPPED\_FAULT |



Use the dashboard to select and inject scenarios.



The safety controller detects unsafe conditions and latches fault states. Returning sensor values to normal does not automatically clear a latched fault or authorize restart.



## 10. Run Demonstrations



### LangGraph diagnostic workflow



```cmd

python day7\_demo.py

```



Demonstrates local AI-assisted diagnosis, maintenance retrieval, structured results, and the diagnostic workflow trace.



### AI diagnosis and behavior-tree simulated recovery



```cmd

python day6\_diagnostic\_demo.py

```



Demonstrates the integrated diagnostic pipeline and operator-controlled simulated recovery.



### Hardened recovery authorization



```cmd

python day10\_demo.py

```



Demonstrates fault-episode binding, one-time approval consumption, replay rejection, and invalidation of stale authorization.



These demonstrations illustrate complementary recovery capabilities; they should not be interpreted as a single production-integrated safety system.



## 11. Tests and Evaluation



### Automated tests



```cmd

python -m pytest -q

```



### Fault detection evaluation



```cmd

python evaluation/evaluate\_faults.py

```



### Safety evaluation



```cmd

python evaluation/evaluate\_safety.py

```



Evaluation artifacts are stored under `evaluation/`, including:



\- `day11\_summary.json`

\- `day11\_diagnostic\_results.csv`

\- `day11\_latency.csv`

\- `workflow\_results.csv`



## 12. Measured Prototype Results



Results obtained from the project's synthetic evaluation and local demonstrations:



| Evaluation | Observed result |

| --- | --- |

| Automated tests | 113 passed |

| Predefined synthetic fault detection | 4/4 correct |

| Synthetic diagnostic scenarios | 4/4 completed and correct |

| Maintenance retrieval Hit@3 | 3/3 |

| Adversarial safety checks | 12/12 unsafe cases blocked |

| Three-run diagnostic latency benchmark | Mean 46.42 seconds |

| Local offline diagnostic demonstration | Completed successfully |



The latency figure is specific to the three-run benchmark and is not a guaranteed response time.



A separate four-scenario diagnostic evaluation recorded approximately 31.9–97.1 seconds per case. Live demonstrations can take longer depending on local model inference.



These results describe a limited synthetic prototype evaluation, not validated real-world industrial performance.



### Evidence limitations



\- The scenario sample size is small.

\- Fault readings and images are simulated.

\- Local inference latency varies.

\- Vision-language output can disagree with deterministic sensor evidence.

\- Maintenance recommendations require human verification.



During one demonstration, the vision model described a simulated jam image as normal. The diagnostic system retained the conflicting evidence instead of allowing the model output to override the deterministic safety state.



## 13. Offline Operation



FactoryGuard AI uses locally installed Ollama models and local Python components.



An offline demonstration was completed with Wi-Fi disabled while the dashboard and Ollama continued running.



The demonstration included:



\- Simulated conveyor-jam fault detection

\- Local Gemma 3 inference

\- Maintenance document retrieval

\- AI-generated maintenance guidance

\- Structured diagnostic output

\- Safety-state preservation

\- Local diagnostic history



Internet access is needed for initial installation, model downloads, and publishing the repository, but not for the demonstrated local inference workflow.



## 14. Safety Architecture and Limitations



\*\*FactoryGuard AI is a software-only research and demonstration prototype. It does not control physical industrial machinery.\*\*



Safety measures demonstrated include:



\- Deterministic sensor thresholds

\- Latched fault states

\- Sensor freshness checks

\- Emergency-stop and guard-interlock checks

\- Operator acknowledgement

\- Explicit recovery approval

\- Fault-episode-bound authorization

\- Rejection of stale and replayed approvals

\- Audit-related authorization checks

\- Separation of AI advice from restart permission



A generated AI recommendation is never sufficient to authorize a machine restart.



Fault resolution and recovery actions are simulated and represent authorized maintenance steps rather than actual mechanical repairs.



This project has not undergone industrial safety certification, hardware validation, or production deployment. It must not be used as a real machine safety controller.



## 15. Screenshots and Demo



Project evidence includes:



\- Dashboard monitoring and scenario injection

\- Normal, jam, overheating, and high-vibration states

\- AI diagnostic reports and retrieved procedures

\- Operator-controlled simulated recovery

\- Safety authorization demonstrations

\- Offline inference demonstration

\- Persistent diagnostic history



Screenshots and demonstration media will be linked or embedded in the published submission.



\*\*Demo video:\*\* To be added after publication.



\*\*Kaggle submission:\*\* To be added after publication.



\*\*GitHub repository:\*\* To be added after publication.



## 16. Project Scope



FactoryGuard AI demonstrates how local AI inference, retrieval-augmented maintenance assistance, deterministic safety enforcement, and human-controlled simulated recovery can coexist within an industrial monitoring prototype.



The objective is not to replace certified safety systems or maintenance professionals. It is to demonstrate a practical separation between probabilistic AI assistance and deterministic safety decisions.



\---



\*\*Hackathon:\*\* GDG Windsor — Build with AI: Smart Automation, Robotics, and Vision



\*\*Project:\*\* FactoryGuard AI



\*\*Deployment:\*\* Local, software-only prototype



