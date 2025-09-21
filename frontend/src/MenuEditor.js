import React from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { Card, Button } from 'react-bootstrap';
import MenuItemModal from './MenuItemModal';

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie('csrftoken');

function MenuEditor() {
  const [menus, setMenus] = React.useState([]);
  const [selectedMenuId, setSelectedMenuId] = React.useState(null);
  const [items, setItems] = React.useState([]);
  const selectedMenu = menus.find(m => m.id === selectedMenuId);
  const [menuName, setMenuName] = React.useState(selectedMenu ? selectedMenu.name : '');

  React.useEffect(() => {
    fetch('http://localhost:8000/api/menus/')
      .then(res => res.json())
      .then(data => {
        const userMenus = data.filter(menu => menu.owner === window.userId);
        setMenus(userMenus);
        if (userMenus.length > 0) {
          setSelectedMenuId(userMenus[0].id);
          setItems(userMenus[0].items);
        }
      });
  }, []);

  React.useEffect(() => {
    const menu = menus.find(m => m.id === selectedMenuId);
    setItems(menu ? menu.items : []);
  }, [selectedMenuId, menus]);

  React.useEffect(() => {
  setMenuName(selectedMenu ? selectedMenu.name : '');
}, [selectedMenu]);

  const [showModal, setShowModal] = React.useState(false);
  const [editingItem, setEditingItem] = React.useState(null);

  function handleSave(item) {
    const payload = { ...item, menu: selectedMenuId };
    console.log('Saving item:', payload);
    if (item.id) {
      // Edit
      fetch(`/api/menu-items/${item.id}/`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(payload),
      })
        .then(res => {
          if (!res.ok) throw new Error('Failed to save');
          return res.json();
        })
        .then(updated => {
          setItems(items.map(i => i.id === updated.id ? updated : i));
          setShowModal(false);
        })
        .catch(err => alert('error saving item: ' + err.message));
    } else {
      // Create
      fetch('/api/menu-items/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(payload),
      })
        .then(res => {
          if (!res.ok) throw new Error('failed to create');
          return res.json();
        })
        .then(created => {
          setItems([...items, created]);
          setShowModal(false);
        })
        .catch(err => alert('Error creating item: ' + err.message));
    }
  }

  function handleDelete(id) {
    fetch(`/api/menu-items/${id}/`, { 
      method: 'DELETE',
      headers: { 'X-CSRFToken': csrftoken },
    })
      .then(() => setItems(items.filter(i => i.id !== id)));
  }

  function onDragEnd(result) {
    if (!result.destination) return;
    const newItems = Array.from(items);
    const [moved] = newItems.splice(result.source.index, 1);
    newItems.splice(result.destination.index, 0, moved);
    setItems(newItems);
  }

  function handleMenuNameSave() {
  if (!selectedMenu) return;
  fetch(`/api/menus/${selectedMenu.id}/`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
    },
    body: JSON.stringify({ ...selectedMenu, name: menuName }),
  })
    .then(res => {
      if (!res.ok) throw new Error('Failed to save menu name');
      return res.json();
    })
    .then(updated => {
      setMenus(menus.map(m => m.id === updated.id ? updated : m));
    })
    .catch(err => alert('Error saving menu name: ' + err.message));
}

  return (
  <div className="container py-4" style={{ maxWidth: '900px' }}>
    {/* Header Card */}
    <div className="card mb-4 shadow-sm border-0" style={{ borderRadius: '16px' }}>
      <div className="card-body">
        <div className="row align-items-center">
          <div className="col-md-8">
            <div className="d-flex align-items-center mb-3">
              <input
                type="text"
                value={menuName}
                onChange={e => setMenuName(e.target.value)}
                className="form-control"
                style={{ fontWeight: 700, fontSize: '1.3em', maxWidth: '320px', marginRight: '1em' }}
              />
              {selectedMenu && (
                <span className={`badge ${selectedMenu.is_active ? 'bg-success' : 'bg-secondary'}`}>
                  {selectedMenu.is_active ? 'Active' : 'Inactive'}
                </span>
              )}
              <Button
                variant="outline-primary"
                size="sm"
                style={{ marginLeft: '1em' }}
                onClick={handleMenuNameSave}
              >
                Save Name
              </Button>
            </div>
            <div className="d-flex gap-2 mb-2">
              <select
                value={selectedMenuId || ''}
                onChange={e => setSelectedMenuId(Number(e.target.value))}
                className="form-select"
                style={{ maxWidth: '260px', fontSize: '1.1em', borderRadius: '8px' }}
              >
                {menus.map(menu => (
                  <option key={menu.id} value={menu.id}>{menu.name}</option>
                ))}
              </select>
              <Button
                onClick={() => { setEditingItem(null); setShowModal(true); }}
                className="mb-0"
                style={{ fontWeight: 500, fontSize: '1em', borderRadius: '8px' }}
              >
                Create Item
              </Button>
            </div>
            {selectedMenu && selectedMenu.items && (
              <div className="mb-2 text-muted" style={{ fontSize: '1em' }}>
                {selectedMenu.items.length} items
              </div>
            )}
          </div>
          <div className="col-md-4 text-center">
            {selectedMenu && selectedMenu.photo && (
              <img
                src={`https://res.cloudinary.com/dgmvyic4g/${selectedMenu.photo}`}
                alt={selectedMenu.name}
                className="img-fluid rounded shadow"
                style={{ maxHeight: '160px', objectFit: 'cover', borderRadius: '12px' }}
              />
            )}
          </div>
        </div>
      </div>
    </div>
    {/* Menu Items Card */}
    <div className="card shadow-sm border-0" style={{ borderRadius: '16px' }}>
      <div className="card-body">
        <MenuItemModal
          show={showModal}
          item={editingItem}
          onSave={handleSave}
          onClose={() => setShowModal(false)}
        />
        <div className="table-responsive">
          <table className="table table-bordered align-middle">
            <thead>
              <tr>
                <th>Image</th>
                <th>Name</th>
                <th>Section</th>
                <th>Price</th>
                <th>Ingredients</th>
                <th>Available</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id}>
                  <td>
                    {typeof item.image === 'string' && item.image.startsWith('https://res.cloudinary.com/') && item.image.trim() !== '' ? (
                      <img
                        src={item.image}
                        alt={item.name}
                        style={{ maxWidth: '60px', maxHeight: '60px', objectFit: 'cover', borderRadius: '8px' }}
                        onError={e => { e.target.onerror = null; e.target.src = '/static/default_profile_pic.png'; }}
                      />
                    ) : (
                      <span className="text-muted">No image</span>
                    )}
                  </td>
                  <td>
                    <input
                      type="text"
                      value={item.name}
                      onChange={e => {
                        const updated = { ...item, name: e.target.value };
                        setItems(items.map(i => i.id === item.id ? updated : i));
                      }}
                      className="form-control form-control-sm"
                      style={{ minWidth: '120px' }}
                    />
                  </td>
                  <td>
                    <input
                      type="text"
                      value={item.section}
                      onChange={e => {
                        const updated = { ...item, section: e.target.value };
                        setItems(items.map(i => i.id === item.id ? updated : i));
                      }}
                      className="form-control form-control-sm"
                      style={{ minWidth: '80px' }}
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      value={item.price}
                      onChange={e => {
                        const updated = { ...item, price: e.target.value };
                        setItems(items.map(i => i.id === item.id ? updated : i));
                      }}
                      className="form-control form-control-sm"
                      style={{ minWidth: '70px' }}
                    />
                  </td>
                  <td>
                    <input
                      type="text"
                      value={item.ingredients}
                      onChange={e => {
                        const updated = { ...item, ingredients: e.target.value };
                        setItems(items.map(i => i.id === item.id ? updated : i));
                      }}
                      className="form-control form-control-sm"
                      style={{ minWidth: '120px' }}
                    />
                  </td>
                  <td>
                    <input
                      type="checkbox"
                      checked={item.is_available}
                      onChange={e => {
                        const updated = { ...item, is_available: e.target.checked };
                        setItems(items.map(i => i.id === item.id ? updated : i));
                      }}
                    />
                  </td>
                  <td>
                    <Button variant="danger" size="sm" onClick={() => handleDelete(item.id)} style={{ borderRadius: '6px', fontWeight: 500, marginRight: '6px' }}>Delete</Button>
                    <Button variant="primary" size="sm" onClick={() => { setEditingItem(item); setShowModal(true); }} style={{ borderRadius: '6px', fontWeight: 500 }}>Edit</Button>
                    <Button variant="success" size="sm" onClick={() => handleSave(item)} style={{ borderRadius: '6px', fontWeight: 500, marginLeft: '6px' }}>Save</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
);
}

export default MenuEditor;