

CRE Kernel – v0.2 Design



> Extending v0.1 authority-based truth resolution into

explicit trust, time-awareness, and safety locking.









---



🎯 Goal of v0.2

s

v0.2 focuses on making truth resolution:



More explicit



More defensive



More explainable



Safer under attack





v0.1 proved authority-based resolution works.

v0.2 formalizes it.





---



🔑 New Concepts Introduced



1\. Explicit Agent Trust Registry



In v0.1:



Agent trust was implicit (hardcoded / assumed)





In v0.2:



Trust becomes first-class data





Each agent has:



agent\_id



trust\_score (0.0 – 1.0)



role (human / system / ai)



created\_at





This allows:



Real authority modeling



Dynamic trust updates



Human > AI precedence







---



2\. Time-Decay on Claims



Old claims should slowly lose power.



Each claim weight becomes:



effective\_weight = agent\_trust × claim\_confidence × time\_decay



Where:



New claims matter more



Old hallucinations fade out



Truth can evolve safely







---



3\. Dispute Locking



If consensus margin is too small:



Entity enters LOCKED state



No new claims can resolve it



Requires human or higher-authority override





This prevents:



Endless flip-flopping



Swarm pressure attacks



Silent corruption







---



🧠 Updated Resolution Flow



1\. Fetch all claims for entity





2\. Apply agent trust





3\. Apply time decay





4\. Aggregate by value





5\. Compute consensus margin





6\. Decide outcome:



RESOLVED



UNKNOWN



LOCKED











---



🛡️ Attacks v0.2 Defends Against



Junior agent spam



Sybil swarm attacks



Long-term memory poisoning



Slow truth drift



High-confidence hallucinations







---



🧩 What v0.2 Does NOT Do (Yet)



No vector search



No embeddings



No LLM prompting



No protocol adapters





Kernel correctness comes first.





---



🛣️ Leads to v0.3



v0.2 enables:



Human override hooks



Audit logs



Dispute review





Which unlocks:



Kernel governance (v0.3)



Federation



Multi-user systems







---



✅ v0.2 Success Criteria



If implemented correctly:



Truth does not drift



Attacks fail safely



Ambiguity is visible



Humans stay in control







---



> Memory lies.

Authority decides.

Kernel enforces.

