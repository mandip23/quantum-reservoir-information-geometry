
# Quantum Reservoir Computing for Early-Warning Detection of Non-Linear Transitions(lorenz system)

This repository implements an open quantum reservoir framework designed to detect early-warning signals (EWS) of critical transitions in non-stationary classical dynamical systems. By injecting a parameter-drifting chaotic Lorenz system into a dissipative(Lindblad Master Equation) 1D transverse-field Ising chain, we analyze how quantum-information-inspired observables track  regime shifts.

# In this project we used the following physics
1.Open Quantum Systems, 
2.Quantum Information Geometry, 
3. Nonlinear Dynamics.

# Scientific Pipeline 


       1. Classical Driver             
  Lorenz System with Parameter Drift
      ρ: 28.0 (Chaos) -> 5.0 (FP)   

                  |
                  | (Continuous Feature Injection)
                  v

       2. Quantum Reservoir           
 Dissipative 1D Transverse Ising    
   Driven by Lindblad Dynamics      

                  |
                  | (Density Matrix  ρ(t))
                  v

   3. Quantum Feature Extraction      
 • Quantum Susceptibility (λ_max)   
 • Magnetization Variance           
 • Quantum Speed Variance           
 • Fidelity Autocorrelation         
                  |
                  v

      4. Criticality Analysis         
  Transition vs. Control Baseline 
  
# mathematical equtions involed in this projects 
1. # Lorenz system equtions
   
   

