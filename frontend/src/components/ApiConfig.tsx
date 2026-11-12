import type { ApiConfigProps } from "../types/recognition";

function ApiConfig({
  endpointUrl,
  setEndpointUrl,
  fileFieldName,
  setFileFieldName,
}: ApiConfigProps) {
  return (
    <div className="collapse mb-3" id="apiConfig">
      <div className="card card-body border-0 shadow-sm bg-white">
        <div className="row g-2 align-items-center">
          <div className="col-md-7">
            <label
              htmlFor="endpointUrl"
              className="form-label small fw-bold mb-1"
            >
              Adres endpointu FastAPI:
            </label>

            <input
              type="text"
              id="endpointUrl"
              className="form-control form-control-sm"
              value={endpointUrl}
              onChange={(e) => setEndpointUrl(e.target.value)}
            />
          </div>

          <div className="col-md-5">
            <label
              htmlFor="fileFieldName"
              className="form-label small fw-bold mb-1"
            >
              Nazwa parametru pliku w FastAPI:
            </label>

            <input
              type="text"
              id="fileFieldName"
              className="form-control form-control-sm"
              value={fileFieldName}
              onChange={(e) => setFileFieldName(e.target.value)}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default ApiConfig;
