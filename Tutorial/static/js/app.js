document.addEventListener('DOMContentLoaded', function () {
    const itemList = document.getElementById('item-list');
    const newItemInput = document.getElementById('new-item');
    const createItemButton = document.getElementById('create-item');

    // Fetch and display items
    function loadItems() {
        fetch('/read')
            .then(response => response.json())
            .then(data => {
                itemList.innerHTML = '';
                data.forEach(item => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <input type="text" value="${item.name}" data-id="${item.id}">
                        <button class="update-item" data-id="${item.id}">Update</button>
                        <button class="delete-item" data-id="${item.id}">Delete</button>
                    `;
                    itemList.appendChild(li);
                });
            });
    }

    // Create a new item
    createItemButton.addEventListener('click', function () {
        const name = newItemInput.value;
        if (name.trim()) {
            fetch('/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: name })
            })
                .then(response => response.json())
                .then(data => {
                    newItemInput.value = '';
                    loadItems();
                });
        }
    });

    // Update an item
    itemList.addEventListener('click', function (e) {
        if (e.target.classList.contains('update-item')) {
            const id = e.target.dataset.id;
            const input = e.target.previousElementSibling;
            const name = input.value;
            fetch(`/update/${id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name: name })
            })
                .then(response => response.json())
                .then(data => loadItems());
        }
    });

    // Delete an item with confirmation
    itemList.addEventListener('click', function (e) {
        if (e.target.classList.contains('delete-item')) {
            const id = e.target.dataset.id;

            // Display confirmation dialog
            const confirmAction = confirm('Are you sure you want to delete this item?');
            
            if (confirmAction) {
                fetch(`/delete/${id}`, {
                    method: 'DELETE'
                })
                    .then(response => response.json())
                    .then(data => loadItems());
            } else {
                // User canceled the deletion, do nothing
                console.log('Deletion canceled');
            }
        }
    });

    // Load items on page load
    loadItems();
});
