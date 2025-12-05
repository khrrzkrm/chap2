structures:
1. Introduction
1.1 Motivation

Responsibility is central in law, ethics, and multi-agent systems. 
Define forward looking as future and backward look as blame assingnement after detecting a violation.

1.2 Relationship to Causality

One paragraph explaining causality in law (sine qua non, NESS).

Clarifies that this report focuses on responsibility attribution, not causal inference.

Causality appears only as a legal component for actionable responsibility.

1.3 Contributions

Formal classification of responsibility types across domains.

Comprehensive logical and algorithmic framework for multi-agent Blame assignement.

Detection of all violations based on time.

Worked examples across several logics using the landlord–tenant scenario.

Identification of expressive gaps (reparations, CTD obligations, proportional liability, etc.).

2. Concepts and Definitions of blame assignement Across Domains
2.1 Blame in Law

Criminal, civil, and administrative responsibility.

Duty of care, omissions, negligence, proximate cause, foreseeability.

Joint and comparative liability.

2.2 Philosophical Blame

Control, moral blame, foreseeability, omissions, reactive attitudes.

Forward-looking vs backward-looking responsibility.

2.3 Blame in Theoretical Computer Science & Formal Verification

Trace-based reasoning.

Responsibility as deviation on traces.

Strategic responsibility (ATL/STIT).

Deontic responsibility for obligations.

Responsibility in runtime verification monitors.

2.4 Multidomain Comparison

Table comparing responsibilities across domains.


3. Classification of Responsibility for Multi-Agent Systems
3.1 By Type

Backward-looking

Forward-looking

Individual vs collective

Omissions vs actions

Strategic ability

Probabilistic responsibility

Duty escalation and secondary obligations

3.2 By Domain in computer science

MAS logics

Formal verification

Software engineering and safety standards

3.3 Requirements for MAS Responsibility Attribution

1- Support for multi-agent traces

2- Detection of multiple violations and quatitative blame score

4- Temporal locality and independence

4- Support for omissions and interference

5- Joint responsibility



5.1 Trace-Based Responsibility Detection (All Violations): Monitoring Norm Violations in Multi-Agent Systems – Bulling, Dastani & Knobbout (2013). This work introduces mechanisms for observing agents’ activities and signaling norm violations
ifaamas.org
, effectively detecting all instances of norm violation in execution traces.

5.2 Backward-Looking Responsibility: Responsibility and Blame: A Structural-Model Approach – Chockler & Halpern (2004). This paper formalizes backward-looking (ex post) responsibility using counterfactual causality, identifying minimal changes in a prior sequence (trace prefix) that would prevent an outcome
ar5iv.labs.arxiv.org
. It provides a measure of an agent’s responsibility based on the smallest deviation needed to avert a violation.

5.3 Strategic Responsibility (ATL/STIT): Strategic Responsibility Under Imperfect Information – Yazdanpanah et al. (2019). This AAMAS 2019 paper extends Alternating-time Temporal Logic (ATL) with STIT (“seeing to it that”) concepts to reason about an agent’s ability vs. actual action in strategic settings
arxiv.org
. It defines criteria for strategy deviation and responsibility attribution in multi-agent games under imperfect information.

5.4 Responsibility for Omissions: The Deliberative STIT: A Study of Action, Omission, Ability, and Obligation – Horty & Belnap (1995). This foundational work in philosophical logic analyzes how an agent’s omission (failure to act) can bear responsibility, given the agent’s duty, opportunity, and capacity to act
ijcai.org
. It formalizes conditions under which not bringing about an outcome (when one had the duty and ability) incurs responsibility.

5.5 Legal NESS Responsibility: Causation in Tort Law – Wright (1985). Wright introduces the NESS test (“Necessary Element of a Sufficient Set”) for legal responsibility, which deems an event a cause of harm if it is a necessary part of some sufficient set of conditions for that harm
scribd.com
. This concept has been used to attribute responsibility in law: a wrongful act is responsible for harm if it was a necessary element of a scenario sufficient to produce the harm.

5.6 Temporal Logic Responsibility (Anticipatory): Anticipating Responsibility in Multiagent Planning – Parker, Grandi & Lorini (2023). This recent work uses Linear Temporal Logic over finite traces (LTL<sub>f</sub>) to formalize anticipatory responsibility, allowing agents to foresee if their actions might lead to future violations
arxiv.org
. It introduces a notion of predictive responsibility (risk scores) and an algorithm (PredResp) to evaluate responsibility for potential future outcomes during planning.

5.7 Probabilistic Responsibility: Responsibility-Aware Strategic Reasoning in Probabilistic MAS – Mu et al. (2024). This research extends ATL to probabilistic systems, defining agents’ responsibility in terms of expected outcomes. It provides a framework where each agent’s strategy optimizes a combination of reward and expected causal responsibility
ar5iv.labs.arxiv.org
, effectively measuring how much an agent’s action reduces expected harm. (See also Chockler & Halpern 2004 for defining degrees of responsibility/blame in probabilistic terms.)

5.8 Action Theories and Dynamic Logic: Causality, Responsibility and Blame in Team Plans – Alechina, Halpern & Logan (2017). This AAMAS paper uses action theories (planning formalisms) to attribute responsibility in multi-agent plans
arxiv.org
. It introduces logical rules linking actions to obligations and specifies how violating a duty can trigger secondary obligations (duty of repair). The approach outlines algorithms (e.g., Resp_AT) to compute responsibility by analyzing causal chains in dynamic action models and specifying reparative duties when norms are breached.


6.   Expressive and Requirements for MAS Responsibility Attribution Gaps in Logical Frameworks

1-What classical logics cannot express from a normative perspective2
2-how they score from 3.3
