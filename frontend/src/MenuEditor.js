import React from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { Card, Button } from 'react-bootstrap';

const initialItems = [
  { id: '1', name: 'Pizza', section: 'Main', price: 10 },
  { id: '2', name: 'Salad', section: 'Starter', price: 5 },
];

function MenuEditor() {
  const [items, setItems] = React.useState(initialItems);

  function onDragEnd(result) {
    if (!result.destination) return;
    const newItems = Array.from(items);
    const [moved] = newItems.splice(result.source.index, 1);
    newItems.splice(result.destination.index, 0, moved);
    setItems(newItems);
  }

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <Droppable droppableId="menu">
        {(provided) => (
          <div ref={provided.innerRef} {...provided.droppableProps}>
            {items.map((item, idx) => (
              <Draggable key={item.id} draggableId={item.id} index={idx}>
                {(provided) => (
                  <Card ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps} className="mb-2">
                    <Card.Body>
                      <Card.Title>{item.name}</Card.Title>
                      <Card.Text>Section: {item.section} | Price: ${item.price}</Card.Text>
                      <Button variant="danger" size="sm">Delete</Button>
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
  );
}

export default MenuEditor;