
# Quantum Reservoir Computing for Detecting Dynamical Regime Changes in the Lorenz System

In this work, presents a quantum reservoir computing framework for investigating whether quantum-information observables extracted from an open quantum system can distinguish stationary chaotic dynamics from continuously drifting nonlinear dynamics.

The project combines nonlinear dynamical systems, open quantum systems, and quantum-information-inspired observables to study how a dissipative quantum reservoir responds to gradual parameter changes in the Lorenz system.

 By inserting a parameter-drifting chaotic Lorenz system into a dissipative(Lindblad Master Equation) transverse-field Ising chain, we analyze how quantum-information-inspired observables track  regime shifts.

#  physics background
1.Open Quantum Systems, 
2.Quantum Information Geometry, 
3. Nonlinear Dynamics.

# Scientific Pipeline 

 1. lorenz system           
      Lorenz System with Parameter Drift
      ρ= 28.0 (Chaos) to 5.0 (FP)   

                  
we generate data from lorenz equation and  Insert into reservoir
                  
 2. Quantum Reservoir           
      Dissipative 1D Transverse Ising    
      Driven by Lindblad Dynamics      

                  
 we get the Density Matrix as output from a quntum reservoir 
                

   3. Quantum Feature Extraction      
      Quantum Susceptibility (λ_max)   
      Magnetization Variance           
      Quantum Speed Variance           
      Fidelity Autocorrelation         
                  
                  
  we calulate the diferent indicator 
                  

   4. Criticality Analysis         
      Transition vs. Control Baseline
      
  graphically analyze the result 
  
### 1. lorenz dynnamic
 A Lorenz system with a continuously varying Rayleigh parameter is used to generate non-stationary dynamics.
 ($\rho_c \approx 24.74$):

$$\frac{dx}{dt} = \sigma(y - x), \quad \frac{dy}{dt} = x(\rho(t) - z) - y, \quad \frac{dz}{dt} = xy - \beta z$$

* **Transition Cohort:** $\rho(t)$ undergoes a nonlinear smoothstep decay profile ($\rho: 28.0 \to 5.0$), triggering Critical Slowing Down (CSD).
* **Control Cohort:** $\rho(t)$ is fixed at $28.0$ to provide a  baseline.

### 2. Dissipative Quantum Reservoir
The quantum hardware substrate consists of an $4$-qubit network evolving via the Lindblad Master Equation:

$$\frac{d\rho}{dt} = -i[H_{\text{sys}} + H_{\text{in}}(t), \rho] + \sum_{k} \left( L_k \rho L_k^\dagger - \frac{1}{2} \{L_k^\dagger L_k, \rho\} \right)$$

* **System Hamiltonian ($H_{\text{sys}}$):** A 1D nearest-neighbor $Z$-$Z$ Ising coupling framework with a global transverse field $X$:
  $$H_{\text{sys}} = J \sum_{i=1}^{N-1} Z_i Z_{i+1} + \Gamma \sum_{i=1}^N X_i$$
* **Input Hamiltonian ($H_{\text{in}}$):** Classical multi-variable arrays are dynamically coupled to the reservoir along the longitudinal axis:
  $$H_{\text{in}}(t) = \alpha \sum_{k=1}^{3} x_k(t) Z_k$$
* **Dissipation Channels ($L_k$):** Includes pure dephasing constraints via $\sqrt{\gamma_{deph}} Z_i$ and energy relaxation pulling states down to the ground state via $\sqrt{\gamma_{relax}} \sigma_i^-$.



##   Quantum Indicators

We extract tracking indicator from the density matrix trajectory $\rho(t)$ using the  expectation value relation $\langle \hat{O} \rangle = \text{Tr}(\rho \hat{O})$:

* **Quantum Susceptibility ($\lambda_{\max}$):** The maximum eigenvalue of the rolling covariance matrix calculated across the collective operator space $\{X_i, Z_i, Z_i Z_{i+1}\}$.
* **Magnetization Variance $\text{Var}(M_{\text{rel}})$:** Moving variance of the aggregate longitudinal magnetization $M = \sum \langle Z_i \rangle$.
* **Quantum Speed Variance $\text{Var}(v_{\text{rel}})$:** Rolling variance of the kinematic state propagation speed calculated via the normalized Frobenius norm:
  $$v(t) = \frac{\|\rho(t) - \rho(t-1)\|_F}{\|\rho(t)\|_F}$$
* **Fidelity Lag-1 Autocorrelation:** The lag-1 Pearson correlation coefficient of consecutive Uhlmann state fidelities:
  $$F(\rho_t, \rho_{t-1}) = \left( \text{Tr} \sqrt{\sqrt{\rho_t} \rho_{t-1} \sqrt{\rho_t}} \right)^2$$
  
##  Result  
![](quantum-reservoir-information-geometry/blob/main/fig.png)


