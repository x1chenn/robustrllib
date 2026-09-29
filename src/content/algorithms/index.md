---
title: All Methods
---

# All Methods

RobustRLlib is organised around **algorithm attribution**. Every method records where robustness enters, which shift it claims to address, and which base algorithm realises it.

<p class="rl-legend"><span class="rl-badge rl-fam-standard">Standard reference</span><span class="rl-badge rl-fam-learner">Learner-centric</span><span class="rl-badge rl-fam-data">Data-centric</span><span class="rl-badge rl-fam-generative">Data-centric · generative</span><span class="rl-badge rl-fam-environment">Environment-centric</span><span class="rl-badge rl-fam-safe">Robust safe</span></p>

## Standard Algorithms

6 methods. See [Standard Algorithms](standard/index.md).

| Method | Family | Setting | Base | Claimed<br>robustness | Shifted-env<br>rollout | Adversarial<br>network | Learned<br>model |
|---|---|---|---|---|:-:|:-:|:-:|
| [**IQL**](standard/iql.md) | <span class="rl-badge rl-fam-standard">Standard reference</span> | Offline | — | — |  |  |  |
| [**TD3+BC**](standard/td3bc.md) | <span class="rl-badge rl-fam-standard">Standard reference</span> | Offline | — | — |  |  |  |
| [**MOPO**](standard/mopo.md) | <span class="rl-badge rl-fam-standard">Standard reference</span> | Offline | SAC | — |  |  |  |
| [**SynthER**](standard/synther.md) | <span class="rl-badge rl-fam-standard">Standard reference</span> | Offline | IQL | — |  |  |  |
| [**PPO**](standard/ppo.md) | <span class="rl-badge rl-fam-standard">Standard reference</span> | Online | — | — |  |  |  |
| [**SAC**](standard/sac.md) | <span class="rl-badge rl-fam-standard">Standard reference</span> | Online | — | — |  |  |  |

## Robust Online Algorithms

5 methods. See [Robust Online Algorithms](robust-online/index.md).

| Method | Family | Base | Claimed<br>robustness | Shifted-env<br>rollout | Adversarial<br>network | Learned<br>model |
|---|---|---|---|:-:|:-:|:-:|
| [**ATLA**](robust-online/atla.md) | <span class="rl-badge rl-fam-learner">Learner-centric</span> | PPO | Observation |  | ✓ |  |
| [**ATLA-SA**](robust-online/atla-sa.md) | <span class="rl-badge rl-fam-learner">Learner-centric</span> | PPO | Observation |  | ✓ |  |
| [**RSC**](robust-online/rsc.md) | <span class="rl-badge rl-fam-learner">Learner-centric</span> | SAC | Semantic |  |  | ✓ |
| [**RARL**](robust-online/rarl.md) | <span class="rl-badge rl-fam-environment">Environment-centric</span> | PPO / TRPO | Dynamic | ✓ | ✓ |  |
| [**DR**](robust-online/dr.md) | <span class="rl-badge rl-fam-environment">Environment-centric</span> | SAC / PPO | Dynamic | ✓ |  |  |

## Robust Offline Algorithms

8 methods. See [Robust Offline Algorithms](robust-offline/index.md).

| Method | Family | Base | Claimed<br>robustness | Shifted-env<br>rollout | Adversarial<br>network | Learned<br>model |
|---|---|---|---|:-:|:-:|:-:|
| [**RFQI**](robust-offline/rfqi.md) | <span class="rl-badge rl-fam-learner">Learner-centric</span> | FQI | Dynamic |  |  |  |
| [**RORL**](robust-offline/rorl.md) | <span class="rl-badge rl-fam-learner">Learner-centric</span> | SAC | Observation |  |  |  |
| [**ATLA-IQL**](robust-offline/atla-iql.md) | <span class="rl-badge rl-fam-learner">Learner-centric</span> | IQL | Observation |  | ✓ |  |
| [**RSC-IQL**](robust-offline/rsc-iql.md) | <span class="rl-badge rl-fam-data">Data-centric</span> | IQL | Semantic |  |  | ✓ |
| [**RAMBO**](robust-offline/rambo.md) | <span class="rl-badge rl-fam-data">Data-centric</span> | SAC | Dynamic |  | ✓ | ✓ |
| [**ROMB**](robust-offline/romb.md) | <span class="rl-badge rl-fam-generative">Generative</span> | IQL | Dynamic |  | ✓ | ✓ |
| [**FWM**](robust-offline/fwm.md) | <span class="rl-badge rl-fam-generative">Generative</span> | IQL | Dynamic |  |  | ✓ |
| [**PLR-PVL**](robust-offline/plr-pvl.md) | <span class="rl-badge rl-fam-generative">Generative</span> | IQL | Dynamic |  |  | ✓ |

## Robust Safe Algorithms

2 methods. See [Robust Safe Algorithms](robust-safe/index.md).

| Method | Family | Base | Claimed<br>robustness | Shifted-env<br>rollout | Adversarial<br>network | Learned<br>model |
|---|---|---|---|:-:|:-:|:-:|
| [**RAMU**](robust-safe/ramu.md) | <span class="rl-badge rl-fam-safe">Robust safe</span> | PPO | Dynamic |  |  |  |
| [**SPiDR**](robust-safe/spidr.md) | <span class="rl-badge rl-fam-safe">Robust safe</span> | PPO | Dynamic | ✓ |  | ✓ |

## How to read the tables

- **Family** says where robustness enters: the learner, the data, a generative model of the data, or the environment that training rollouts come from.
- **Base** is the algorithm a method is built on. A robust method and its base are trained and evaluated under the same protocol.
- **Claimed robustness** is the shift the original paper targets.
- **Shifted-env rollout** marks rollouts collected from a deliberately perturbed environment. Offline methods learn from fixed nominal data, so it is never ticked for them.
- **Adversarial network** marks a learned adversary optimised against the policy.
- **Learned model** marks a trained next-state predictor used by the robustness mechanism.
