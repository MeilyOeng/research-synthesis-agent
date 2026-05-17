import './Home.css';
import Sidebar from './Sidebar';

function Home() {
  return (
    <div className="body">
      <Sidebar />
      <div className="flex flex-col flex-1 p-6">
        <p className="title text-lg mb-4">
          What can I help with?
        </p>
        <div className="input-wrapper">
          <textarea className="form-control" id="Ask" placeholder="Ask anything"></textarea>
          <button type="button" className="btn btn-primary">
            <i className="material-icons">arrow_upward</i>
          </button>
        </div>
      </div>
    </div>
  );
}

export default Home;
