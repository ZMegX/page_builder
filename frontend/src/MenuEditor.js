import React from 'react';
import { Tabs, Tab, Button, Toast, ToastContainer } from 'react-bootstrap';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import MenuItemModal from './MenuItemModal';

function MenuEditor({ menu }) {
  // Toast state
  const [toast, setToast] = React.useState({ show: false, message: '', variant: 'success' });
  const [savingOrder, setSavingOrder] = React.useState(false);
  const [lastReorderedIds, setLastReorderedIds] = React.useState([]);
  const [menus, setMenus] = React.useState(menu ? [menu] : []);
  const [selectedMenuId, setSelectedMenuId] = React.useState(menu ? menu.id : null);
  const [items, setItems] = React.useState([]);
  const selectedMenu = menus.find(m => m.id === selectedMenuId);
  const [menuName, setMenuName] = React.useState(selectedMenu ? selectedMenu.name : '');

  React.useEffect(() => {
    if (menu) {
      setMenus([menu]);
      setSelectedMenuId(menu.id);
      setItems(menu.items || []);
    } else {
      fetch('http://localhost:8000/menus/api/menus/')
        .then(res => res.json())
        .then(data => {
          const userMenus = data.filter(menu => menu.owner === window.userId);
          setMenus(userMenus);
          if (userMenus.length > 0) {
            setSelectedMenuId(userMenus[0].id);
            setItems(userMenus[0].items);
          }
          // Check for ?addItem=1 in URL
          const params = new URLSearchParams(window.location.search);
          if (params.get('addItem') === '1') {
            setEditingItem(null);
            setShowModal(true);
          }
        });
    }
  }, [menu]);

  React.useEffect(() => {
    const menu = menus.find(m => m.id === selectedMenuId);
    setItems(menu ? menu.items : []);
  }, [selectedMenuId, menus]);

  React.useEffect(() => {
    setMenuName(selectedMenu ? selectedMenu.name : '');
  }, [selectedMenu]);

  const [showModal, setShowModal] = React.useState(false);
  const [editingItem, setEditingItem] = React.useState(null);
  const [activeSection, setActiveSection] = React.useState('');
  const [showInfoBanner, setShowInfoBanner] = React.useState(true);
  const [unsavedItemIds, setUnsavedItemIds] = React.useState([]);

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

  function handleSave(item) {
    const payload = { ...item, menu: selectedMenuId };
    if (item.id) {
      // Edit
  fetch(`/menus/api/menu-items/${item.id}/`, {
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
          setUnsavedItemIds(unsavedItemIds.filter(id => id !== updated.id));
          setShowModal(false);
          setToast({ show: true, message: 'Item saved successfully!', variant: 'success' });
        })
        .catch(err => setToast({ show: true, message: 'Error saving item: ' + err.message, variant: 'danger' }));
    } else {
      // Create
  fetch('/menus/api/menu-items/', {
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
          setToast({ show: true, message: 'Item created successfully!', variant: 'success' });
        })
        .catch(err => setToast({ show: true, message: 'Error creating item: ' + err.message, variant: 'danger' }));
    }
  }

  function handleDelete(id) {
  fetch(`/menus/api/menu-items/${id}/`, { 
      method: 'DELETE',
      headers: { 'X-CSRFToken': csrftoken },
    })
      .then(res => {
        if (!res.ok) throw new Error('Failed to delete');
        setItems(items.filter(i => i.id !== id));
        setToast({ show: true, message: 'Item deleted.', variant: 'success' });
      })
      .catch(err => setToast({ show: true, message: 'Error deleting item: ' + err.message, variant: 'danger' }));
  }

  // Drag-and-drop reordering within section
  function onDragEnd(result) {
    if (!result.destination) return;
    const section = activeSection;
    const sectionItems = sectionMap[section] || [];
    if (result.source.index === result.destination.index) return;
    const reordered = Array.from(sectionItems);
    const [moved] = reordered.splice(result.source.index, 1);
    reordered.splice(result.destination.index, 0, moved);
    // Update items in state
    // Replace only the items in this section, keep others unchanged
    const newItems = items.filter(i => (i.section || 'Uncategorized') !== section)
      .concat(reordered);
    setItems(newItems);
    setLastReorderedIds(reordered.map(i => i.id));
    setToast({ show: true, message: 'Items reordered. Click "Save Order" to persist.', variant: 'info' });
    // Optionally auto-save (comment out next line to disable auto-save)
    // handleSaveOrder(section, reordered);
    // Highlight for 1.5s
    setTimeout(() => setLastReorderedIds([]), 1500);
  }

  function handleSaveOrder(section, reorderedItems) {
    setSavingOrder(true);
    const orderPayload = (reorderedItems || (sectionMap[section] || [])).map((item, idx) => ({ id: item.id, order: idx }));
  fetch('/menus/api/menu-items/reorder/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
      },
      body: JSON.stringify(orderPayload),
    })
      .then(res => {
        if (!res.ok) throw new Error(`Failed to save order for ${section}`);
        return res.json();
      })
      .then(() => {
        setToast({ show: true, message: `Order saved for ${section}!`, variant: 'success' });
      })
      .catch(err => {
        setToast({ show: true, message: `Error saving order for ${section}: ${err.message}`, variant: 'danger' });
      })
      .finally(() => setSavingOrder(false));
  // Remove stray bracket here
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

  // Section descriptions
  const sectionDescriptions = {
    'breakfast': 'Breakfast: Morning favorites and classics.',
    'main': 'Main Courses: Entrées and signature dishes.',
    'lunch': 'Lunch: Midday meals and specials.',
    'dinner': 'Dinner: Evening selections and chef specials.',
    'dessert': 'Dessert: Sweets and treats.',
    'drinks': 'Drinks: Beverages and refreshments.',
    'appetizers': 'Appetizers: Starters and small plates.',
    'sides': 'Sides: Complementary dishes.',
    'specials': 'Specials: Limited-time offerings.',
    'vegan': 'Vegan: Plant-based options.',
    'gluten_free': 'Gluten Free: Wheat-free choices.',
    'kids': "Kids' Menu: Child-friendly meals.",
    'hot_drinks': 'Hot Drinks: Coffee, tea, and more.',
    'Uncategorized': 'Uncategorized: Items without a section.'
  };

  // Group items by section
  const sectionMap = {};
  items.forEach(item => {
    const section = item.section || 'Uncategorized';
    if (!sectionMap[section]) sectionMap[section] = [];
    sectionMap[section].push(item);
  });
  const sections = Object.keys(sectionMap);
  React.useEffect(() => {
    if (sections.length > 0 && !activeSection) setActiveSection(sections[0]);
  }, [sections, activeSection]);

  // Section choices to pass to modal
  const [sectionChoices, setSectionChoices] = React.useState([]);

  React.useEffect(() => {
  fetch('/menus/api/menu-sections/')
      .then(res => res.json())
      .then(data => {
        // Expecting [{ value: 'breakfast', label: 'Breakfast' }, ...]
        setSectionChoices(data);
      })
      .catch(() => {
        // fallback to default if fetch fails
        setSectionChoices([
          { value: 'breakfast', label: 'Breakfast' },
          { value: "main", label: "Main Courses" },
          { value: 'lunch', label: 'Lunch' },
          { value: 'dinner', label: 'Dinner' },
          { value: 'dessert', label: 'Dessert' },
          { value: 'drinks', label: 'Drinks' },
          { value: 'appetizers', label: 'Appetizers' },
          { value: 'sides', label: 'Sides' },
          { value: 'specials', label: 'Specials' },
          { value: 'vegan', label: 'Vegan' },
          { value: 'gluten_free', label: 'Gluten Free' },
          { value: 'kids', label: "Kids' Menu" },
          { value: 'hot_drinks', label: 'Hot Drinks' }
        ]);
      });
  }, []);

  return (
    <div className="container py-4" style={{ maxWidth: '900px' }}>
      {/* Info Banner for Action Guidance */}
      {showInfoBanner && (
        <div className="alert alert-info alert-dismissible fade show mb-3" role="alert" style={{ borderRadius: '12px', fontSize: '1.08em' }}>
          <strong>How to use:</strong> Edit item names inline. Click <b>Edit</b> for full details. Drag to reorder.
          <button type="button" className="btn-close" aria-label="Close" onClick={() => setShowInfoBanner(false)} style={{ float: 'right' }}></button>
        </div>
      )}
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
      {/* Menu Items Card with Tabs */}
      <div className="card shadow-sm border-0" style={{ borderRadius: '16px' }}>
        <div className="card-body">
          <MenuItemModal
            show={showModal}
            item={editingItem}
            onSave={handleSave}
            onClose={() => setShowModal(false)}
            sectionChoices={sectionChoices}
          />
          <DragDropContext onDragEnd={onDragEnd}>
            <Tabs activeKey={activeSection} onSelect={setActiveSection} className="mb-3">
              {sections.map(section => (
                <Tab
                  eventKey={section}
                  key={section}
                  title={
                    <span title={sectionDescriptions[section] || ''} style={{ cursor: 'help' }}>
                      {section}
                    </span>
                  }
                >
                  {/* Section description below tab title */}
                  <div className="mb-2 text-muted" style={{ fontSize: '0.98em' }}>
                    {sectionDescriptions[section]}
                  </div>
                  {sectionMap[section].length === 0 ? (
                    <div className="alert alert-info text-center" style={{ borderRadius: '8px' }}>
                      No items in this section yet. Click <b>'Create Item'</b> to add one.
                    </div>
                  ) : (
                    <>
                      <div className="d-flex mb-2 align-items-center gap-2">
                        <Button
                          variant="primary"
                          size="sm"
                          disabled={savingOrder || !(selectedMenu && selectedMenu.is_active)}
                          onClick={() => handleSaveOrder(section)}
                        >
                          {savingOrder ? (
                            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          ) : null}
                          Save Order
                        </Button>
                        {!selectedMenu?.is_active && (
                          <span className="text-danger" style={{ fontSize: '0.95em' }}>Menu is inactive. Drag-and-drop disabled.</span>
                        )}
                      </div>
                      <Droppable droppableId={section} direction="vertical" isDropDisabled={!selectedMenu?.is_active}>
                        {(provided) => (
                          <div className="table-responsive" ref={provided.innerRef} {...provided.droppableProps}>
                            <table className="table table-bordered align-middle">
                              <thead>
                                <tr>
                                  <th style={{ width: '40px' }}></th>
                                  <th>Image</th>
                                  <th>Name</th>
                                  <th>Actions</th>
                                </tr>
                              </thead>
                              <tbody>
                                {sectionMap[section].map((item, idx) => {
                                  const isUnsaved = unsavedItemIds.includes(item.id);
                                  const isReordered = lastReorderedIds.includes(item.id);
                                  return (
                                    <Draggable key={item.id} draggableId={String(item.id)} index={idx} isDragDisabled={!selectedMenu?.is_active}>
                                      {(provided, snapshot) => (
                                        <tr
                                          ref={provided.innerRef}
                                          {...provided.draggableProps}
                                          style={{
                                            ...provided.draggableProps.style,
                                            borderLeft: isUnsaved ? '6px solid #ffe066' : isReordered ? '6px solid #0d6efd' : undefined,
                                            background: isUnsaved ? '#fffbe6' : isReordered ? '#e7f1ff' : undefined,
                                            boxShadow: snapshot.isDragging ? '0 2px 12px #e9ecef' : undefined
                                          }}
                                        >
                                          <td {...provided.dragHandleProps} style={{ cursor: selectedMenu?.is_active ? 'grab' : 'not-allowed', textAlign: 'center', fontSize: '1.2em', color: '#adb5bd' }} title={selectedMenu?.is_active ? 'Drag to reorder' : 'Menu is inactive'}>
                                            &#9776;
                                          </td>
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
                                            <div style={{ display: 'flex', alignItems: 'center' }}>
                                              <input
                                                type="text"
                                                value={item.name}
                                                onChange={e => {
                                                  const updated = { ...item, name: e.target.value };
                                                  setItems(items.map(i => i.id === item.id ? updated : i));
                                                  if (!unsavedItemIds.includes(item.id)) {
                                                    setUnsavedItemIds([...unsavedItemIds, item.id]);
                                                  }
                                                }}
                                                className="form-control form-control-sm"
                                                style={{ minWidth: '120px' }}
                                              />
                                              {isUnsaved && (
                                                <span title="Unsaved changes" style={{ color: '#ffc107', marginLeft: '6px', fontSize: '1.2em' }}>
                                                  &#9888;
                                                </span>
                                              )}
                                              {isReordered && (
                                                <span title="Reordered" style={{ color: '#0d6efd', marginLeft: '6px', fontSize: '1.2em' }}>
                                                  &#8635;
                                                </span>
                                              )}
                                            </div>
                                          </td>
                                          <td>
                                            <Button variant="primary" size="sm" onClick={() => { setEditingItem(item); setShowModal(true); }} style={{ borderRadius: '6px', fontWeight: 500 }}>Edit</Button>
                                            <Button variant="danger" size="sm" onClick={() => handleDelete(item.id)} style={{ borderRadius: '6px', fontWeight: 500, marginLeft: '6px' }}>Delete</Button>
                                            <Button variant="success" size="sm" onClick={() => handleSave(item)} style={{ borderRadius: '6px', fontWeight: 500, marginLeft: '6px' }}>Save</Button>
                                          </td>
                                        </tr>
                                      )}
                                    </Draggable>
                                  );
                                })}
                                {provided.placeholder}
                              </tbody>
                            </table>
                          </div>
                        )}
                      </Droppable>
                    </>
                  )}
                </Tab>
              ))}
            </Tabs>
          </DragDropContext>
      {/* Toast notifications */}
      <ToastContainer position="top-end" className="p-3">
        <Toast
          show={toast.show}
          onClose={() => setToast({ ...toast, show: false })}
          bg={toast.variant}
          delay={3200}
          autohide
        >
          <Toast.Body className={toast.variant === 'danger' ? 'text-white' : ''}>{toast.message}</Toast.Body>
        </Toast>
      </ToastContainer>
        </div>
      </div>
    </div>
  );
}

export default MenuEditor;

