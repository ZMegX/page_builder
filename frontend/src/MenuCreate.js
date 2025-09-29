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

const MenuCreate = ({ onCreated }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
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
      const response = await axios.post('/api/menus/', {
        name,
        description,
      }, {
        headers: { 'X-CSRFToken': csrftoken }
      });
      setSuccess('Menu created successfully!');
      setName('');
      setDescription('');
      if (onCreated) onCreated(response.data);
      // Redirect to menu editor after short delay
      setTimeout(() => navigate('/menu-editor'), 1200);
    } catch (err) {
      setError('Failed to create menu.');
    }
    setIsSubmitting(false);
  };

  return (
    <div className="container py-4">
      <h2>Create New Menu</h2>
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
    </div>
  );
};

export default MenuCreate;