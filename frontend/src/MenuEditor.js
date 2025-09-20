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
                {selectedMenu && (
                  <span className={`badge ${selectedMenu.is_active ? 'bg-success' : 'bg-secondary'}`}>{selectedMenu.is_active ? 'Active' : 'Inactive'}</span>
                )}
              </div>
              <div className="d-flex gap-2 mb-2">
                <select value={selectedMenuId || ''} onChange={e => setSelectedMenuId(Number(e.target.value))} className="form-select" style={{ maxWidth: '260px', fontSize: '1.1em', borderRadius: '8px' }}>
                  {menus.map(menu => (
                    <option key={menu.id} value={menu.id}>{menu.name}</option>
                  ))}
                </select>
                <Button onClick={() => { setEditingItem(null); setShowModal(true); }} className="mb-0" style={{ fontWeight: 500, fontSize: '1em', borderRadius: '8px' }}>Create Item</Button>
              </div>
              {selectedMenu && selectedMenu.items && (
                <div className="mb-2 text-muted" style={{ fontSize: '1em' }}>{selectedMenu.items.length} items</div>
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

      {/* Menu Items Card */}
      <div className="card shadow-sm border-0" style={{ borderRadius: '16px' }}>
        <div className="card-body">
          <MenuItemModal
            show={showModal}
            item={editingItem}
            onSave={handleSave}
            onClose={() => setShowModal(false)}
          />
          <DragDropContext onDragEnd={onDragEnd}>
            <Droppable droppableId="menu" direction="horizontal">
              {(provided) => (
                <div ref={provided.innerRef} {...provided.droppableProps} style={{ display: 'flex', flexWrap: 'wrap', gap: '18px', minHeight: '120px' }}>
                  {items.map((item, idx) => (
                    <Draggable key={item.id} draggableId={item.id} index={idx}>
                      {(provided) => (
                        <Card ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps} style={{ minWidth: '220px', maxWidth: '260px', flex: '1 1 220px', marginBottom: '0', boxShadow: '0 2px 8px rgba(0,0,0,0.08)', borderRadius: '10px', border: '1px solid #e3e3e3', background: '#fff', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                          {typeof item.image === 'string' && item.image.startsWith('https://res.cloudinary.com/') && item.image.trim() !== '' ? (
                            <div className="card-img-top" style={{ textAlign: 'center', marginTop: '12px' }}>
                              <img
                                src={item.image}
                                alt={item.name}
                                style={{ maxWidth: '100%', maxHeight: '120px', objectFit: 'cover', borderRadius: '8px', boxShadow: '0 1px 4px rgba(0,0,0,0.07)' }}
                                onError={e => { e.target.onerror = null; e.target.src = '/static/default_profile_pic.png'; }}
                              />
                            </div>
                          ) : null}
                          <Card.Body style={{ padding: '14px 12px 10px 12px', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                            <Card.Title style={{ fontWeight: 600, fontSize: '1.08em', marginBottom: '6px' }}>{item.name}</Card.Title>
                            <Card.Text style={{ fontSize: '0.98em', color: '#555', marginBottom: '8px' }}>Section: <span style={{ fontWeight: 500 }}>{item.section}</span> | Price: <span style={{ color: '#007bff', fontWeight: 600 }}>${item.price}</span></Card.Text>
                            <div style={{ display: 'flex', gap: '8px', marginTop: 'auto' }}>
                              <Button variant="danger" size="sm" onClick={() => handleDelete(item.id)} style={{ borderRadius: '6px', fontWeight: 500 }}>Delete</Button>
                              <Button onClick={() => { setEditingItem(item); setShowModal(true); }} size="sm" style={{ borderRadius: '6px', fontWeight: 500, background: '#f8f9fa', color: '#007bff', border: '1px solid #007bff' }}>Edit</Button>
                            </div>
                          </Card.Body>
                        </Card>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>
        </div>
      </div>
    </div>
  );
}

export default MenuEditor;