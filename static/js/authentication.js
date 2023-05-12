'use strict'

// ___Подія для першої сторінки і сторінки забув пароль__

// переміні форми authentication__login
const LoginForm = document.querySelector('#authentication__login')
const forgotBtn = document.querySelector('#authentication__login-forgot')
const inputUsername = document.querySelector('#authentication-input__username')
const inputPassword = document.querySelector('#authentication-input__password')
const loginBtn = document.querySelector('#authentication__login-button')
const loginRegistrationBtn = document.querySelector('#authentication__login-registration')

// переміні форми authentication__password
const passwordForm = document.querySelector('#authentication__password')
const backBtn = document.querySelector('#authentication__password-back')

// переміні форми authentication__registration
const registrationForm = document.querySelector('#authentication__registration')
const registrationBackBtn = document.querySelector('#authentication__registration-back')


// Подія для кнопки *Back to Log In*
forgotBtn.addEventListener('click', () => {
  LoginForm.style.display = 'none'
  passwordForm.style.display = 'flex'
})

// Подія для кнопки *Forgot password?*
backBtn.addEventListener('click', () => {
  passwordForm.style.display = 'none'
  LoginForm.style.display = 'flex'
})

// Подія для кнопки *Log in*
loginBtn.addEventListener('click', (e) => {
  // Виключив перезагрузку сторінки при кліку
  e.preventDefault()

  // провірка чи є якийсь текст в інпутах при нажаті на кнопку
  if (inputUsername.value && inputPassword.value) {
    LoginForm.style.display = 'none'
    emailAddressBlock.style.display = 'flex'
  }
})

// Подія для кнопки *Registration*
loginRegistrationBtn.addEventListener('click', () => {
  LoginForm.style.display = 'none'
  registrationForm.style.display = 'flex'
})

// Подія для кнопки *Log In* з форми *Registration*
registrationBackBtn.addEventListener('click', () => {
  LoginForm.style.display = 'flex'
  registrationForm.style.display = 'none'
})

// _______перемені форми authentication__email____

// переміні блоку authentication__email-address
const emailAddressBlock = document.querySelector('#authentication__email-address')
const addressInput = document.querySelector('#authentication__address-input')
const addressBtn = document.querySelector('#authentication__address-btn')

// переміні блоку authentication__email-code
const emailCodeBlock = document.querySelector('#authentication__email-code')
const codeInput = document.querySelector('#authentication__code-input')
const emailCodeText = document.querySelector('#authentication__box-span')
const emailCodeBtn = document.querySelector('#authentication__email-button')
const emailCodeError = document.querySelector('#authentication__code-error')


// Подія для кнопки *Send Code*
addressBtn.addEventListener('click', () => {

  // перевірка чи є якийсь текст в інпуті при нажаті на кнопку
  if (addressInput.value) {
    emailAddressBlock.style.display = 'none'
    emailCodeBlock.style.display = 'flex'

    // введену пошту в *authentication__address-input* вставляю в subtitle/span наступного відкривающогося блока *authentication__email-code*
    emailCodeText.textContent = addressInput.value
  }
})

// времений код вивода ошибки при підтвердженні коду яких приходить на пошту
emailCodeBtn.addEventListener('click', (e) => {
  codeInput.value = ''
  codeInput.focus()
  codeInput.classList.add('authentication-input__error')
  // codeInput.setAttribute('placeholder', 'Incorrect verification password')
  emailCodeError.style.display = 'flex'

  emailCodeBtn.classList.add('authentication-btn__error')
})