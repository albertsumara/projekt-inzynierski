function Navbar() {
  return (
    <nav className="navbar navbar-dark bg-success shadow-sm mb-4">
      <div className="container">
        <span className="navbar-brand fw-bold">
          System rekomendacji potraw – prototyp systemu rozpoznawania obrazów
        </span>

        <a
          className="btn btn-outline-light btn-sm"
          href="#apiConfig"
          data-bs-toggle="collapse"
          role="button"
          aria-expanded="false"
          aria-controls="apiConfig"
        >
          Ustawienia Endpointu
        </a>
      </div>
    </nav>
  );
}

export default Navbar;
