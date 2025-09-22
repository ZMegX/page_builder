import React, { useState, useEffect } from 'react';
import { Modal, Button, Form } from 'react-bootstrap';

function MenuItemModal({ show, item, onSave, onClose }) {
  const SECTION_CHOICES = [
    { value: 'breakfast', label: 'Breakfast' },
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
  ];
  const [form, setForm] = useState({
    name: '',
    section: 'breakfast',
    price: '',
    ingredients: '',
    is_available: true,
    image: '',
    is_popular: false,
  });

  useEffect(() => {
    if (item) {
      setForm({
        name: item.name || '',
        section: item.section || 'breakfast',
        price: item.price || '',
        ingredients: item.ingredients || '',
        is_available: item.is_available !== undefined ? item.is_available : true,
        image: item.image || '',
        is_popular: item.is_popular !== undefined ? item.is_popular : false,

      });
    } else {
      setForm({
        name: '',
        section: 'breakfast',
        price: '',
        ingredients: '',
        is_available: true,
        image: '',
        is_popular: false,
      });
    }
  }, [item, show]);

  function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('upload_preset', 'react_upload_menuItem'); 

    fetch('https://api.cloudinary.com/v1_1/dgmvyic4g/image/upload', {
      method: 'POST',
      body: formData,
    })
      .then(res => res.json())
      .then(data => {
        setForm(f => ({ ...f, image: data.secure_url }));      });
  }

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    setForm(f => ({
      ...f,
      [name]: type === 'checkbox' ? checked : value,
    }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    const payload = { ...form };
    if (item && item.id) payload.id = item.id;
    onSave(payload);
  }

  return (
    <Modal show={show} onHide={onClose}>
      <Form onSubmit={handleSubmit}>
        <Modal.Header closeButton>
          <Modal.Title>{item ? 'Edit Item' : 'Create Item'}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {/* Card-style image preview above form fields */}
          {form.image && (
            <div className="card-img-top mb-3" style={{ textAlign: 'center' }}>
              <img src={form.image} alt="Menu Item" style={{ maxWidth: '100%', maxHeight: '180px', objectFit: 'cover', borderRadius: '8px' }} />
            </div>
          )}
          <Form.Group className="mb-3">
            <Form.Label>Name</Form.Label>
            <Form.Control name="name" value={form.name} onChange={handleChange} required />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Check
              type="checkbox"
              label="Popular Dish"
              name="is_popular"
              checked={form.is_popular}
              onChange={handleChange}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Section</Form.Label>
             <Form.Select name="section" value={form.section} onChange={handleChange}>
              {SECTION_CHOICES.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </Form.Select>
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Price</Form.Label>
            <Form.Control name="price" type="number" step="0.01" value={form.price} onChange={handleChange} required />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Ingredients</Form.Label>
            <Form.Control name="ingredients" value={form.ingredients} onChange={handleChange} />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Image</Form.Label>
            <Form.Control type="file" accept="image/*" onChange={handleImageUpload} />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Check
              type="checkbox"
              label="Available"
              name="is_available"
              checked={form.is_available}
              onChange={handleChange}
            />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button variant="primary" type="submit">{item ? 'Save Changes' : 'Create'}</Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}

export default MenuItemModal;