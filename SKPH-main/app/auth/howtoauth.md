# Jak używać auth
### Wymagane importy w zależności od potrzeb:
```
from flask_login import login_required, current_user
from app.auth.user_service import roles_required
```
### 1. Żeby zabezpieczyć route przed niezalogowanymi użytkownikami użyj: 
```
@login_required
```
Przykład użycia:
```
@bp.route('/logout')
@login_required
def logout():
    ...
```
### 2. Żeby zabezpieczyć route tylko dla wybranych typów użytkowników użyj:
```
@roles_required('admin')
```
lub w przypadku wielu ról z możliwością dostępu:
```
@roles_required(['admin', 'volunteer']) 
```
Przykład użycia:
```
@bp.route('/manage_users', methods=['GET', 'POST'])
@roles_required('admin')
def manage_users():
    ...
```
### 3. Żeby odwoływać się do pól aktualnie zalogowanego użytkownika użyj:
```
current_user
```
Przykład użycia w kodzie:
```
if current_user.type == 'authorities':
    authority = current_user.authorities
    if authority and not authority.approved:
        flash('You do not have permission to access this page.', 'danger')
```
Przykład użycia w html'u:
```
{% if current_user.is_authenticated %}
<div class="navbar-text mr-3">
  {{ current_user.email }} ({{ current_user.type }})
```
