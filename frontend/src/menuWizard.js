import React, { useState } from 'react';
import MenuCreate from './MenuCreate';
import MenuEditor from './MenuEditor';

const MenuWizard = () => {
  const [menu, setMenu] = useState(null);

  // Step 1: Create menu
  if (!menu) {
    return (
      <MenuCreate
        onCreated={createdMenu => setMenu(createdMenu)}
      />
    );
  }

  // Step 2: Add items to menu
  return (
    <MenuEditor
      menu={menu}
    />
  );
};

export default MenuWizard;