// CampusConnect - adds a "show / hide" eye button to every password field
// (login and register pages), so you can check what you typed.
document.querySelectorAll('input[type="password"]').forEach(input => {
  const group = document.createElement('div');
  group.className = 'input-group';
  input.parentNode.insertBefore(group, input);
  group.appendChild(input);

  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'btn btn-outline-secondary';
  btn.setAttribute('aria-label', 'Show password');
  btn.innerHTML = '<i class="bi bi-eye"></i>';   // fixed markup, no user data

  btn.addEventListener('click', () => {
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    btn.firstElementChild.className = show ? 'bi bi-eye-slash' : 'bi bi-eye';
    btn.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
  });

  group.appendChild(btn);
});