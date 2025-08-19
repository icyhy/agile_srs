import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null
  }),
  
  actions: {
    setUser(user) {
      this.user = user
    },
    
    setToken(token) {
      this.token = token
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    },
    
    logout() {
      this.user = null
      this.setToken(null)
    }
  },
  
  getters: {
    isAuthenticated: (state) => !!state.token,
    userInfo: (state) => state.user
  }
})

export const useRequirementStore = defineStore('requirement', {
  state: () => ({
    requirements: [],
    currentRequirement: null
  }),
  
  actions: {
    setRequirements(requirements) {
      this.requirements = requirements
    },
    
    setCurrentRequirement(requirement) {
      this.currentRequirement = requirement
    },
    
    addRequirement(requirement) {
      this.requirements.push(requirement)
    },
    
    updateRequirement(requirement) {
      const index = this.requirements.findIndex(r => r.id === requirement.id)
      if (index !== -1) {
        this.requirements[index] = requirement
      }
    }
  }
})