import numpy as np 
def lorenz_equations(state,sigma=10,rho=28,beta=8/3):
    x,y,z=state
    return np.array([sigma*(y-x),x*(rho-z)-y,x*y-beta*z])

def runge_kutta4(n_steps=10000,dt1=0.001,rho=28):
    state=np.array([1,1,1])
    series=[]
    for _ in range(10000):
      k1=lorenz_equations(state,rho=rho)
      k2=lorenz_equations(state+0.5*dt1*k1,rho=rho)
      k3=lorenz_equations(state+0.5*dt1*k2,rho=rho)
      k4=lorenz_equations(state+dt1*k3,rho=rho)
      state = state+dt1/6*(k1+2*k2+2*k3+k4)


    
    for _ in range(n_steps):
      k1=lorenz_equations(state,rho=rho)
      k2=lorenz_equations(state+0.5*dt1*k1,rho=rho)
      k3=lorenz_equations(state+0.5*dt1*k2,rho=rho)
      k4=lorenz_equations(state+dt1*k3,rho=rho)
      state = state+dt1/6*(k1+2*k2+2*k3+k4)
      series.append(state.copy())
    
    return np.array(series)

def regim_change(nstep=5000,rho1=28,rho2=15):
   regim1=runge_kutta4(n_steps=nstep,rho=rho1)
   regim2=runge_kutta4(n_steps=nstep,rho=rho2)
   time_sries=np.concatenate([regim1,regim2])
   return time_sries,nstep
