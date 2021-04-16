import React, { useEffect, useState } from 'react';
import './navbar.scss';
import { Navbar, Nav, NavDropdown } from 'react-bootstrap';
import { useLocation } from 'react-router-dom';

function NavBar() {
  let location = useLocation();
  const [authenticated, setAuthenticated] = useState(
    localStorage.getItem('access_token') !== null
  );
  const [role] = useState(localStorage.getItem('role'));

  useEffect(() => {
    setAuthenticated(localStorage.getItem('access_token') !== null);
  }, [location]);

  return (
    <Navbar>
      <Navbar.Collapse>
        <Navbar.Brand href="/">FireApp</Navbar.Brand>
        {authenticated && role === 'ADMIN' && (
          <NavDropdown
            title="Reference Data"
            id="basic-nav-dropdown"
            className={'white'}>
            <NavDropdown.Item href="/reference/roles">Roles</NavDropdown.Item>
            <NavDropdown.Item href="/reference/qualifications">
              Qualifications
            </NavDropdown.Item>
            <NavDropdown.Item href="/reference/asset_types">
              Asset Types
            </NavDropdown.Item>
          </NavDropdown>
        )}
        <Nav className="ml-auto navbar-right">
          {authenticated ? (
            <Nav.Link href="/logout">Logout</Nav.Link>
          ) : (
            <Nav.Link href="/login">Login</Nav.Link>
          )}
        </Nav>
      </Navbar.Collapse>
    </Navbar>
  );
}
export default NavBar;
