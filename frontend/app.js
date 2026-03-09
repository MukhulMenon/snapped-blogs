const express = require("express");
const app = express();
const axios = require("axios");
const methodOverride = require("method-override");
const multer = require("multer");
const upload = multer({ storage: multer.memoryStorage() }); 
const FormData = require("form-data");

app.set("view engine", "ejs");
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(methodOverride("_method"));

const BASE_URL = process.env.BACKEND_URL || "http://127.0.0.1:8000";

// node-fetch loader (only if you're not on Node 18+ native fetch)
const fetchFn = (...args) =>
  import("node-fetch").then(({ default: fetch }) => fetch(...args));

async function getJson(url) {
  const resp = await fetchFn(url, { method: "GET" });

  // Handle non-2xx responses cleanly
  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    throw new Error(`Backend error ${resp.status} ${resp.statusText}: ${text}`);
  }

  return resp.json();
}

app.get("/", async (req, res) => {
  try {
    // Pass data into EJS (adjust variable name to your template needs)
    res.render("index");
  } catch (error) {
    console.error("Error fetching data:", error);
    res.status(500).send("Error fetching API data");
  }
});

app.get("/blog-list", async (req, res) => {
  try {
    const resp = await getJson(`${BASE_URL}/blog-list`);
    // Flask returns: { message: "...", data: [ ... ] }
    const blogs = resp?.data ?? [];
    res.render("blogs-page", { blogs, BASE_URL });
  } catch (error) {
    console.error("Error fetching data:", error);
    res.status(500).send("Error fetching API data");
  }
});

app.get("/blog-list/:id", async (req, res) => {
  try {
    const postId = req.params.id;
    const data = await getJson(`${BASE_URL}/blog-list/${encodeURIComponent(postId)}`);
    res.render("blog", { blog_post: data, BASE_URL });
  } catch (error) {
    console.error("Error fetching blog post:", error);
    res.status(500).send("Error fetching blog post");
  }
});

app.get("/create-blog", async (req, res) => {
  try {
    res.render("new-blog");
  } catch (error) {
    console.error("Error fetching data:", error);
    res.status(500).send("Error fetching API data");
  }
});

app.post("/create-blog/submit", upload.single("image"), async (req, res) => {
  try {
    if (!req.file) return res.status(400).send("Image is required");

    const formData = new FormData();
    formData.append("name", req.body.name);
    formData.append("summary", req.body.summary);
    formData.append("description", req.body.description);
    formData.append("date", req.body.date);

    // append the file buffer; form-data accepts a Buffer and options
    formData.append("image", req.file.buffer, {
      filename: req.file.originalname,
      contentType: req.file.mimetype,
      knownLength: req.file.size,
    });

    // forward to Flask create-blog/submit
    const resp = await axios.post(`${BASE_URL}/create-blog/submit`, formData, {
      headers: formData.getHeaders(),
      maxBodyLength: Infinity,
      maxContentLength: Infinity,
      validateStatus: status => status < 500, // allow 4xx for nicer handling
    });

    if (resp.status >= 400) {
      console.error("Backend error creating blog:", resp.status, resp.data);
      return res.status(500).send(`Error creating blog: ${JSON.stringify(resp.data)}`);
    }

    // resp.data should be the created doc (because Flask now returns JSON)
    const newId = resp.data?._id || resp.data?.data?._id;
    if (newId) return res.redirect(`/blog-list/${newId}`);

    // fallback: go to list
    return res.redirect("/blog-list");
  } catch (error) {
    console.error("Error creating blog:", {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
    });
    return res
      .status(500)
      .send(`Error creating blog: ${error.response?.data?.error || error.message}`);
  }
});

app.post("/blog-list/:id", async (req, res) => {
  try {
    const { id } = req.params;

    // Since your Flask delete is POST (Option A)
    await axios.post(`${BASE_URL}/blog-list/${encodeURIComponent(id)}`);

    // Redirect back to list
    return res.redirect("/blog-list");
  } catch (err) {
    console.error("Delete failed:", {
      message: err?.message,
      code: err?.code,
      status: err?.response?.status,
      data: err?.response?.data,
    });

    return res
      .status(500)
      .send(`Error deleting blog: ${err?.response?.data?.error || err?.message}`);
  }
});

app.get("/image/:id", async (req, res) => {
  try {
    const { id } = req.params;

    const resp = await axios.get(`${BASE_URL}/image/${encodeURIComponent(id)}`, {
      responseType: "stream",
    });

    // forward content-type so browser knows it's an image
    res.setHeader("Content-Type", resp.headers["content-type"] || "application/octet-stream");

    resp.data.pipe(res);
  } catch (err) {
    console.error("Image proxy failed:", err.message);
    res.status(404).send("Image not found");
  }
});

// (don’t forget to start the server somewhere)
app.listen(3000, () => console.log("Server running on http://localhost:3000"));