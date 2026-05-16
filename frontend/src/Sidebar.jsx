import { useState } from 'react';
import './Sidebar.css';

const Sidebar = () => {
    const [open, setOpen] = useState(true);
    const Menus = [
      { title: 'New Chat', icon: 'edit_square' },
      { title: 'Search Chats', icon: 'search' },
      { title: 'Settings', icon: 'settings', gap: true },
      { title: 'Logout', icon: 'logout' },
    ];

    return (
        <div className={`sidebar h-screen relative duration-300 ${open ? 'w-72' : 'w-15 sidebar-closed'}`}>
        <button
          onClick={() => setOpen(!open)}
          className="sidebar-toggle"
        >
          <i className="material-icons">menu</i>
        </button>

        <div className="sidebar-header">
          <h1 className="sidebar-title">MyApp</h1>
        </div>

        <ul className="sidebar-list">
          {Menus.map((Menu, index) => (
            <li
              key={index}
              className={`sidebar-item ${Menu.gap ? 'sidebar-item-gap' : 'sidebar-item-normal'} ${
                index === 0 ? 'sidebar-item-active' : ''
              }`}
            >
              <span className="sidebar-icon">
                <i className="material-icons">{Menu.icon}</i>
              </span>

              <span className="sidebar-label">{Menu.title}</span>
            </li>
          ))}
        </ul>
      </div>
    );
};

export default Sidebar;