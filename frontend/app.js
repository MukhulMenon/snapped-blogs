const express = require("express");
const app = express();
const axios = require("axios");
const methodOverride = require("method-override");

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
    const data = await getJson(`${BASE_URL}/blog-list`);

    // You used response.data previously; keep that if your API returns { data: [...] }
    const blogs = data?.data ?? data;
    res.render("blogs-page", { blogs });
  } catch (error) {
    console.error("Error fetching data:", error);
    res.status(500).send("Error fetching API data");
  }
});

app.get("/blog-list/:id", async (req, res) => {
  try {
    const postId = req.params.id;
    const data = await getJson(`${BASE_URL}/blog-list/${encodeURIComponent(postId)}`);
    res.render("blog", { blog_post: data });
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

app.post("/create-blog/submit", async (req, res) => {
  try {
    const blogData = {
      name: req.body.name,
      summary: req.body.summary,
      description: req.body.description,
      date: req.body.date,
      image_url: req.body.image_url,
    };

    const resp = await axios.post(`${BASE_URL}/create-blog`, blogData, {
      headers: { "Content-Type": "application/json" },
    });

    return res.redirect("/blog-list/:id");
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

app.post("/blog-list/:id/delete", async (req, res) => {
  try {
    const { id } = req.params;

    // Call Python API to delete
    await axios.delete(`${BASE_URL}/blog-list/${id}`);

    // Redirect after delete (go home or list page)
    return res.redirect("/");
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

// (don’t forget to start the server somewhere)
app.listen(3000, () => console.log("Server running on http://localhost:3000"));