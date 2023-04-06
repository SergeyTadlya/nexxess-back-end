'use strict'

const LoginForm = document.querySelector('#authentication__login')
const forgotBtn = document.querySelector('#authentication__login-forgot')
const passwordForm = document.querySelector('#authentication__password')
const backBtn = document.querySelector('#authentication__password-back')

forgotBtn.addEventListener('click', () => {
  LoginForm.style.display = 'none'
  passwordForm.style.display = 'flex'
})

backBtn.addEventListener('click', () => {
  passwordForm.style.display = 'none'
  LoginForm.style.display = 'flex'
})

const inputUsername = document.querySelector('#authentication-input__username')
const inputPassword = document.querySelector('#authentication-input__password')
const loginBtn = document.querySelector('#authentication__login-button')
const emailAddressBlock = document.querySelector(
  '#authentication__email-address'
)
const emailCodeBlock = document.querySelector('#authentication__email-code')
const addressInput = document.querySelector('#authentication__address-input')
const addressBtn = document.querySelector('#authentication__address-btn')
const codeInput = document.querySelector('#authentication__code-input')

loginBtn.addEventListener('click', (e) => {
  e.preventDefault()

  if (inputUsername.value && inputPassword.value) {
    LoginForm.style.display = 'none'
    emailAddressBlock.style.display = 'flex'
  }
})

addressBtn.addEventListener('click', () => {
  if (addressInput.value) {
    emailAddressBlock.style.display = 'none'
    emailCodeBlock.style.display = 'flex'
  }
})