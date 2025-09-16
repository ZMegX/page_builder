import React, { useState, useEffect } from 'react';
import { Modal, Button, Form } from 'react-bootstrap';

function MenuItemModal({ show, item, onSave, onClose }) {
  const [form, setForm] = useState({
    name: '',
    section: 'breakfast',
    price: '',
    ingredients: '',
    is_available: true,
  });

  useEffect(() => {
    if (item) {
      setForm({
        name: item.name || '',
        section: item.section || 'breakfast',
        price: item.price || '',
        ingredients: item.ingredients || '',
        is_available: item.is_available !== undefined ? item.is_available : true,
      });
    } else {
      setForm({
        name: '',
        section: 'breakfast',
        price: '',
        ingredients: '',
        is_available: true,
      });
    }
  }, [item, show]);

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
          <Form.Group className="mb-3">
            <Form.Label>Name</Form.Label>
            <Form.Control name="name" value={form.name} onChange={handleChange} required />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Section</Form.Label>
            <Form.Select name="section" value={form.section} onChange={handleChange}>
              <option value="breakfast">Breakfast</option>
              <option value="lunch">Lunch</option>
              <option value="dinner">Dinner</option>
              <option value="dessert">Dessert</option>
              <option value="drinks">Drinks</option>
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