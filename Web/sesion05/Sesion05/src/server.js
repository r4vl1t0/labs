const express = require("express");
const cookieParser = require("cookie-parser");
const jwt = require("jsonwebtoken");
const { randomUUID } = require("crypto");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, "..", "public")));

const labs = {
  lab1Student: {
    username: "user",
    password: "987654321",
    secret: "student-normal-secret",
    initialRole: "user",
    requiredRole: "superadministrator",
    flag: "FLAG{lab1_student_none_alg_vertical_privilege_escalation}"
  },
  lab1Professor: {
    username: "test",
    password: "qwerty",
    secret: "professor-normal-secret",
    initialRole: "teacher",
    requiredRole: "master",
    flag: "FLAG{lab1_professor_none_alg_vertical_privilege_escalation}"
  },
  lab2Student: {
    username: "user",
    password: "987654321",
    secret: "umehmc14",
    initialRole: "user",
    requiredRole: "superadministrator",
    flag: "FLAG{lab2_student_weak_jwt_secret}"
  },
  lab2Professor: {
    username: "test",
    password: "qwerty",
    secret: "bestfriend",
    initialRole: "teacher",
    requiredRole: "master",
    flag: "FLAG{lab2_professor_weak_jwt_secret}"
  }
};

const resetUsers = {
  administrator: {
    username: "administrator",
    email: "administrator@local.lab",
    password: "admin-start",
    otp: "7314",
    flag: "FLAG{lab3_insecure_reset_flow_otp_bruteforce}"
  }
};

const sessions = new Map();
const finalUsers = {
  administrator: {
    username: "administrator",
    password: "disabled-until-reset",
    otp: "5876",
    role: "administrator"
  }
};

function base64urlJson(value) {
  return Buffer.from(JSON.stringify(value)).toString("base64url");
}

function signNone(payload) {
  return `${base64urlJson({ alg: "none", typ: "JWT" })}.${base64urlJson(payload)}.`;
}

function decodeJwtWithoutVerification(token) {
  try {
    return jwt.decode(token) || null;
  } catch {
    return null;
  }
}

function vulnerableJwtAuth(config, allowNone) {
  return (req, res, next) => {
    const authHeader = req.headers.authorization || "";
    const token = authHeader.startsWith("Bearer ") ? authHeader.slice(7) : "";
    if (!token) {
      return res.status(401).json({ code: "AUTH_TOKEN_MISSING", message: "Sesion requerida." });
    }

    try {
      const decodedHeader = JSON.parse(Buffer.from(token.split(".")[0], "base64url").toString("utf8"));
      if (allowNone && decodedHeader.alg === "none") {
        req.user = decodeJwtWithoutVerification(token);
        return next();
      }
      req.user = jwt.verify(token, config.secret, { algorithms: ["HS256"] });
      next();
    } catch {
      res.status(401).json({ code: "AUTH_TOKEN_INVALID", message: "Sesion invalida." });
    }
  };
}

function requireRole(requiredRole) {
  return (req, res, next) => {
    if (!req.user || req.user.role !== requiredRole) {
      return res.status(403).json({
        code: `AUTH_ROLE_${requiredRole.toUpperCase()}_REQUIRED`,
        message: "No tiene permisos para completar esta accion."
      });
    }
    next();
  };
}

function createJwtLabRoutes(prefix, config, options) {
  const router = express.Router();

  router.post("/login", (req, res) => {
    const { username, password } = req.body;
    if (username !== config.username || password !== config.password) {
      return res.status(401).json({ code: "LOGIN_FAILED", message: "Credenciales invalidas." });
    }

    const token = jwt.sign(
      { sub: username, username, role: config.initialRole, lab: prefix },
      config.secret,
      { algorithm: "HS256", expiresIn: "2h" }
    );
    res.json({ token, user: { username, role: config.initialRole } });
  });

  router.get("/profile", vulnerableJwtAuth(config, options.allowNone), (req, res) => {
    res.json({ username: req.user.username, role: req.user.role, status: "active" });
  });

  router.post(
    "/admin/report",
    vulnerableJwtAuth(config, options.allowNone),
    requireRole(config.requiredRole),
    (req, res) => {
      res.json({
        ok: true,
        title: "Reporte administrativo",
        flag: config.flag
      });
    }
  );

  app.use(`/api/${prefix}`, router);
}

createJwtLabRoutes("lab1/student", labs.lab1Student, { allowNone: true });
createJwtLabRoutes("lab1/professor", labs.lab1Professor, { allowNone: true });
createJwtLabRoutes("lab2/student", labs.lab2Student, { allowNone: false });
createJwtLabRoutes("lab2/professor", labs.lab2Professor, { allowNone: false });

app.post("/api/lab3/login", (req, res) => {
  const { username, password } = req.body;
  const user = resetUsers[username];
  if (!user || user.password !== password) {
    return res.status(401).json({ code: "LOGIN_FAILED", message: "Credenciales invalidas." });
  }
  const token = jwt.sign({ username, role: "administrator" }, "lab3-session-secret", { expiresIn: "2h" });
  res.json({ token, user: { username, role: "administrator" } });
});

app.post("/api/lab3/forgot", (req, res) => {
  const { username } = req.body;
  if (!resetUsers[username]) {
    return res.status(200).json({ message: "Si la cuenta existe, se enviara un codigo." });
  }
  res.json({ message: "Codigo enviado al correo registrado." });
});

app.post("/api/lab3/reset", (req, res) => {
  const { username, otp, newPassword } = req.body;
  const user = resetUsers[username];
  if (!user) {
    return res.status(404).json({ code: "RESET_ACCOUNT_NOT_FOUND", message: "Solicitud invalida." });
  }
  if (otp !== user.otp) {
    return res.status(400).json({ code: "RESET_OTP_INVALID", message: "Codigo invalido." });
  }
  user.password = newPassword || "changed";
  res.json({ ok: true, message: "Clave actualizada." });
});

app.get("/api/lab3/admin", (req, res) => {
  const authHeader = req.headers.authorization || "";
  const token = authHeader.startsWith("Bearer ") ? authHeader.slice(7) : "";
  try {
    const user = jwt.verify(token, "lab3-session-secret");
    if (user.role !== "administrator") {
      return res.status(403).json({ code: "ADMIN_ONLY", message: "Acceso denegado." });
    }
    res.json({ ok: true, flag: resetUsers.administrator.flag });
  } catch {
    res.status(401).json({ code: "AUTH_TOKEN_INVALID", message: "Sesion invalida." });
  }
});

function sessionMiddleware(req, res, next) {
  let sid = req.query.sid || req.cookies.sid;
  if (!sid) {
    sid = randomUUID();
  }
  if (!sessions.has(sid)) {
    sessions.set(sid, { authenticated: false, username: null, createdAt: Date.now() });
  }
  res.cookie("sid", sid, { httpOnly: false, sameSite: "lax" });
  req.sessionId = sid;
  req.session = sessions.get(sid);
  next();
}

app.use("/api/lab4", sessionMiddleware);

app.get("/api/lab4/session", (req, res) => {
  res.json({ sid: req.sessionId, authenticated: req.session.authenticated, username: req.session.username });
});

app.post("/api/lab4/login", (req, res) => {
  const { username, password } = req.body;
  if (username !== "user" || password !== "987654321") {
    return res.status(401).json({ code: "LOGIN_FAILED", message: "Credenciales invalidas." });
  }
  req.session.authenticated = true;
  req.session.username = username;
  res.json({ ok: true, sid: req.sessionId, user: { username } });
});

app.get("/api/lab4/account", (req, res) => {
  if (!req.session.authenticated) {
    return res.status(401).json({ code: "SESSION_REQUIRED", message: "Inicie sesion." });
  }
  res.json({
    username: req.session.username,
    account: "Cuenta personal",
    flag: "FLAG{lab4_session_fixation}"
  });
});

app.get("/sse", (req, res) => {
  res.sendFile(path.join(__dirname, "..", "public", "final.html"));
});

app.post("/api/final/login", (req, res) => {
  const { username, password } = req.body;
  const user = finalUsers[username];
  if (!user || user.password !== password) {
    return res.status(401).json({ code: "LOGIN_FAILED", message: "Credenciales invalidas." });
  }
  const token = jwt.sign(
    { username, role: user.role, area: "sse" },
    "milutlv141193",
    { algorithm: "HS256", expiresIn: "2h" }
  );
  res.json({ token, user: { username, role: user.role } });
});

app.post("/api/final/forgot", (req, res) => {
  const { username } = req.body;
  if (!finalUsers[username]) {
    return res.status(200).json({ message: "Si la cuenta existe, se enviara un codigo." });
  }
  res.json({ message: "Codigo enviado al correo registrado." });
});

app.post("/api/final/reset", (req, res) => {
  const { username, otp, newPassword } = req.body;
  const user = finalUsers[username];
  if (!user) {
    return res.status(404).json({ code: "RESET_ACCOUNT_NOT_FOUND", message: "Solicitud invalida." });
  }
  if (otp !== user.otp) {
    return res.status(400).json({ code: "RESET_OTP_INVALID", message: "Codigo invalido." });
  }
  user.password = newPassword || "changed";
  res.json({ ok: true, message: "Clave actualizada." });
});

function finalAuth(req, res, next) {
  const authHeader = req.headers.authorization || "";
  const token = authHeader.startsWith("Bearer ") ? authHeader.slice(7) : "";
  try {
    req.user = jwt.verify(token, "milutlv141193", { algorithms: ["HS256"] });
    next();
  } catch {
    res.status(401).json({ code: "AUTH_TOKEN_INVALID", message: "Sesion invalida." });
  }
}

app.get("/api/final/messages", finalAuth, (req, res) => {
  res.json({ items: [] });
});

app.get("/api/final/posts", finalAuth, (req, res) => {
  res.json({ items: [] });
});

app.post("/api/final/command", finalAuth, (req, res) => {
  if (req.user.role !== "master") {
    return res.status(403).json({ code: "ROLE_MASTER_REQUIRED", message: "Se necesita rol master." });
  }
  if (req.body.command !== "cat flag.txt") {
    return res.status(400).json({ code: "COMMAND_NOT_ALLOWED", message: "Comando no permitido." });
  }
  res.json({ output: "FLAG{final_sse_reset_jwt_crack_master_command}" });
});

app.use((req, res) => {
  res.status(404).sendFile(path.join(__dirname, "..", "public", "404.html"));
});

app.listen(PORT, () => {
  console.log(`Auth labs listening on port ${PORT}`);
});
