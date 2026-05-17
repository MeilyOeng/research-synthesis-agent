import { useState } from 'react';
import './R_Sidebar.css';

const R_Sidebar = () => {
    const [open, setOpen] = useState(true);

    return (
        <div className={`rsidebar h-screen relative duration-300 ${open ? 'w-55' : 'w-15 rsidebar-closed'}`}>
          <div className="rsidebar-header">
            <button onClick={() => setOpen(!open)} className="rsidebar-toggle" type="button">
              <i className="material-icons">menu</i>
            </button>
            <h1 className="rsidebar-title"></h1>
          </div>
          <div className="rsidebar-panels">
          <div className="rsidebar-box source-box">
           <h4> Sources </h4>
          </div>
          <div className="rsidebar-box quality-score-box">
           <h4> Quality Score </h4>
          </div>
          <div className="rsidebar-box upload-box">
           <h4> Upload </h4>
          </div>
          </div>
      </div>
    );
};

export default R_Sidebar;
