import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

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

const DEFAULT_ITEM = {
  name: '',
  section: 'breakfast',
  price: '',
  ingredients: '',
  is_available: true,
  image: '',
  is_popular: false,
};

const MenuCreate = ({ onCreated }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [menu, setMenu] = useState(null);
  const [items, setItems] = useState([]);
  const [editingIndex, setEditingIndex] = useState(null);
  const [itemForm, setItemForm] = useState(DEFAULT_ITEM);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');
    setSuccess('');
    if (!name.trim()) {
      setError('Menu name is required.');
      setIsSubmitting(false);
      return;
    }
    try {
      const response = await axios.post('/menus/api/menus/', {
        name,
        description,
      }, {
        headers: { 'X-CSRFToken': csrftoken }
      });
      setSuccess('Menu created successfully!');
      setMenu(response.data);
      setName('');
      setDescription('');
      if (onCreated) onCreated(response.data);
    } catch (err) {
      setError('Failed to create menu.');
    }
    setIsSubmitting(false);
  };

  const handleItemChange = (e) => {
    const { name, value, type, checked } = e.target;
    setItemForm(f => ({
      ...f,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleAddItem = async (e) => {
    e.preventDefault();
    setError('');
    if (!itemForm.name.trim()) {
      setError('Item name is required.');
      return;
    }
    if (!itemForm.price || isNaN(itemForm.price) || Number(itemForm.price) <= 0) {
      setError('Price must be a positive number.');
      return;
    }
    try {
      const payload = { ...itemForm, menu: menu.id };
      const response = await axios.post('/menus/api/menu-items/', payload, {
        headers: { 'X-CSRFToken': csrftoken }
      });
      setItems([...items, response.data]);
      setItemForm(DEFAULT_ITEM);
      setEditingIndex(null);
      setError('');
    } catch (err) {
      setError('Failed to add item.');
    }
  };

  const handleEditItem = (idx) => {
    setEditingIndex(idx);
    setItemForm(items[idx]);
  };

  const handleUpdateItem = async (e) => {
    e.preventDefault();
    setError('');
    if (!itemForm.name.trim()) {
      setError('Item name is required.');
      return;
    }
    if (!itemForm.price || isNaN(itemForm.price) || Number(itemForm.price) <= 0) {
      setError('Price must be a positive number.');
      return;
    }
    try {
      const payload = { ...itemForm, menu: menu.id };
      const response = await axios.put(`/menus/api/menu-items/${itemForm.id}/`, payload, {
        headers: { 'X-CSRFToken': csrftoken }
      });
      const updatedItems = [...items];
      updatedItems[editingIndex] = response.data;
      setItems(updatedItems);
      setItemForm(DEFAULT_ITEM);
      setEditingIndex(null);
      setError('');
    } catch (err) {
      setError('Failed to update item.');
    }
  };

  const handleDeleteItem = async (idx) => {
    const item = items[idx];
    try {
      await axios.delete(`/menus/api/menu-items/${item.id}/`, {
        headers: { 'X-CSRFToken': csrftoken }
      });
      setItems(items.filter((_, i) => i !== idx));
    } catch (err) {
      setError('Failed to delete item.');
    }
  };

  return (
    <div className="container py-4">
      <h2>Create New Menu</h2>
      {!menu ? (
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label">Menu Name</label>
            <input
              type="text"
              className="form-control"
              value={name}
              onChange={e => setName(e.target.value)}
              required
              disabled={isSubmitting}
            />
          </div>
          <div className="mb-3">
            <label className="form-label">Description</label>
            <textarea
              className="form-control"
              value={description}
              onChange={e => setDescription(e.target.value)}
              disabled={isSubmitting}
            />
          </div>
          {error && <div className="alert alert-danger">{error}</div>}
          {success && <div className="alert alert-success">{success}</div>}
          <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
            {isSubmitting ? (
              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            ) : null}
            {isSubmitting ? 'Creating...' : 'Create Menu'}
          </button>
        </form>
      ) : (
        <>
          <h4 className="mt-4">Add Menu Items</h4>
          <form onSubmit={editingIndex === null ? handleAddItem : handleUpdateItem} className="mb-3">
            <div className="row g-2">
              <div className="col-md-3">
                <input
                  type="text"
                  name="name"
                  className="form-control"
                  placeholder="Item Name"
                  value={itemForm.name}
                  onChange={handleItemChange}
                  required
                />
              </div>
              <div className="col-md-2">
                <select
                  name="section"
                  className="form-select"
                  value={itemForm.section}
                  onChange={handleItemChange}
                >
                  <option value="breakfast">Breakfast</option>
                  <option value="main">Main Courses</option>
                  <option value="lunch">Lunch</option>
                  <option value="dinner">Dinner</option>
                  <option value="dessert">Dessert</option>
                  <option value="drinks">Drinks</option>
                  <option value="appetizers">Appetizers</option>
                  <option value="sides">Sides</option>
                  <option value="specials">Specials</option>
                  <option value="vegan">Vegan</option>
                  <option value="gluten_free">Gluten Free</option>
                  <option value="kids">Kids' Menu</option>
                  <option value="hot_drinks">Hot Drinks</option>
                </select>
              </div>
              <div className="col-md-2">
                <input
                  type="number"
                  name="price"
                  className="form-control"
                  placeholder="Price"
                  value={itemForm.price}
                  onChange={handleItemChange}
                  required
                  min="0.01"
                  step="0.01"
                />
              </div>
              <div className="col-md-3">
                <input
                  type="text"
                  name="ingredients"
                  className="form-control"
                  placeholder="Ingredients"
                  value={itemForm.ingredients}
                  onChange={handleItemChange}
                />
              </div>
              <div className="col-md-2 d-flex align-items-center">
                <input
                  type="checkbox"
                  name="is_available"
                  checked={itemForm.is_available}
                  onChange={handleItemChange}
                  className="form-check-input me-2"
                />
                <span>Available</span>
              </div>
            </div>
            <div className="row mt-2">
              <div className="col-md-2">
                <input
                  type="checkbox"
                  name="is_popular"
                  checked={itemForm.is_popular}
                  onChange={handleItemChange}
                  className="form-check-input me-2"
                />
                <span>Popular</span>
              </div>
              <div className="col-md-4">
                <input
                  type="text"
                  name="image"
                  className="form-control"
                  placeholder="Image URL"
                  value={itemForm.image}
                  onChange={handleItemChange}
                />
              </div>
              <div className="col-md-6 text-end">
                <button type="submit" className="btn btn-success">
                  {editingIndex === null ? 'Add Item' : 'Update Item'}
                </button>
                {editingIndex !== null && (
                  <button type="button" className="btn btn-secondary ms-2" onClick={() => { setEditingIndex(null); setItemForm(DEFAULT_ITEM); }}>
                    Cancel
                  </button>
                )}
              </div>
            </div>
            {error && <div className="alert alert-danger mt-2">{error}</div>}
          </form>
          <table className="table table-bordered">
            <thead>
              <tr>
                <th>Name</th>
                <th>Section</th>
                <th>Price</th>
                <th>Ingredients</th>
                <th>Available</th>
                <th>Popular</th>
                <th>Image</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item, idx) => (
                <tr key={item.id || idx}>
                  <td>{item.name}</td>
                  <td>{item.section}</td>
                  <td>{item.price}</td>
                  <td>{item.ingredients}</td>
                  <td>{item.is_available ? 'Yes' : 'No'}</td>
                  <td>{item.is_popular ? 'Yes' : 'No'}</td>
                  <td>{item.image ? <img src={item.image} alt="" style={{ maxWidth: 40, maxHeight: 40 }} /> : '—'}</td>
                  <td>
                    <button className="btn btn-sm btn-primary me-2" onClick={() => handleEditItem(idx)}>Edit</button>
                    <button className="btn btn-sm btn-danger" onClick={() => handleDeleteItem(idx)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <button className="btn btn-primary mt-3" onClick={() => navigate('/menu-editor')}>Go to Menu Editor</button>
        </>
      )}
    </div>
  );
};

export default MenuCreate;