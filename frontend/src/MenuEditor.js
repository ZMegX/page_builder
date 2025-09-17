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

  const [showModal, setShowModal] = React.useState(false);
  const [editingItem, setEditingItem] = React.useState(null);

  function handleSave(item) {
    // Always include menu field in payload
    const payload = { ...item, menu: selectedMenuId };
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
        .then(res => res.json())
        .then(updated => setItems(items.map(i => i.id === updated.id ? updated : i)));
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
        .then(res => res.json())
        .then(created => setItems([...items, created]));
    }
    setShowModal(false);
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

  return (
    <>
      {selectedMenu && selectedMenu.photo && (
        <img
          src={`https://res.cloudinary.com/dgmvyic4g/${selectedMenu.photo}`}
          alt={selectedMenu.name}
          style={{ width: '200px', marginBottom: '16px', objectFit: 'cover', borderRadius: '8px' }}
        />
      )}
      <select value={selectedMenuId || ''} onChange={e => setSelectedMenuId(Number(e.target.value))}>
        {menus.map(menu => (
          <option key={menu.id} value={menu.id}>{menu.name}</option>
        ))}
      </select>
      <Button onClick={() => { setEditingItem(null); setShowModal(true); }} className="mb-3">Create Item</Button>
      <MenuItemModal
        show={showModal}
        item={editingItem}
        onSave={handleSave}
        onClose={() => setShowModal(false)}
      />
      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="menu">
          {(provided) => (
            <div ref={provided.innerRef} {...provided.droppableProps}>
              {items.map((item, idx) => (
                <Draggable key={item.id} draggableId={item.id} index={idx}>
                  {(provided) => (
                    <Card ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps} className="mb-2">
                      {/* Improved Cloudinary image logic */}
                      {typeof item.image === 'string' && item.image.startsWith('https://res.cloudinary.com/') && item.image.trim() !== '' ? (
                        <div className="card-img-top" style={{ textAlign: 'center', marginTop: '12px' }}>
                          <img
                            src={item.image}
                            alt={item.name}
                            style={{ maxWidth: '100%', maxHeight: '180px', objectFit: 'cover', borderRadius: '8px' }}
                            onError={e => { e.target.onerror = null; e.target.src = '/static/default_profile_pic.png'; }}
                          />
                        </div>
                      ) : null}
                      <Card.Body>
                        <Card.Title>{item.name}</Card.Title>
                        <Card.Text>Section: {item.section} | Price: ${item.price}</Card.Text>
                        <Button variant="danger" size="sm" onClick={() => handleDelete(item.id)}>Delete</Button>
                        <Button onClick={() => { setEditingItem(item); setShowModal(true); }} className="ms-2">Edit</Button>
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
    </>
  );
}

export default MenuEditor;