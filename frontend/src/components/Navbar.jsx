import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
    const { user, logout } = useAuth();

    return (
        <nav className="bg-white shadow">
            <div className="container mx-auto px-4">
                <div className="flex justify-between items-center h-16">
                    <Link to="/" className="font-bold text-xl">SafeNetAI</Link>
                    <div className="flex items-center gap-4">
                        {user ? (
                            <>
                                <Link to="/" className="hover:text-blue-600">Dashboard</Link>
                                <Link to="/submit" className="hover:text-blue-600">New Transaction</Link>
                                <button onClick={logout} className="hover:text-blue-600">Logout</button>
                            </>
                        ) : (
                            <>
                                <Link to="/login" className="hover:text-blue-600">Login</Link>
                                <Link to="/register" className="hover:text-blue-600">Register</Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}
