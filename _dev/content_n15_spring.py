"""Spring Boot lessons 6-15."""
from content_js_sql import M

META = [
    M("spring-security-jwt", "spring", "Spring Security and JWT", 18, "Intermediate", "Lock down endpoints, hash passwords and authenticate with a Bearer token.", ["Configure SecurityFilterChain", "Hash with BCrypt", "Validate a JWT"]),
    M("spring-validation-errors", "spring", "Validation and Problem Details", 15, "Intermediate", "Bean Validation, MethodArgumentNotValidException and RFC 7807 bodies.", ["Annotate a DTO", "Return ProblemDetail", "Map a domain error"]),
    M("spring-transactions", "spring", "Transactions and Locking", 16, "Intermediate", "@Transactional boundaries, isolation and optimistic locking.", ["Mark a service transactional", "Use @Version", "Avoid self-invocation"]),
    M("spring-caching", "spring", "Caching with Spring Cache", 14, "Intermediate", "@Cacheable, @CacheEvict and a Redis cache manager.", ["Cache a method", "Evict on write", "Switch to Redis"]),
    M("spring-actuator", "spring", "Actuator, Health and Metrics", 15, "Intermediate", "Expose health, info and Prometheus metrics without leaking internals.", ["Add Actuator", "Customise health", "Scrape metrics"]),
    M("spring-openapi", "spring", "OpenAPI with springdoc", 14, "Intermediate", "Generate Swagger UI from your controllers and document security.", ["Add springdoc", "Annotate operations", "Show a Bearer scheme"]),
    M("spring-files-scheduling", "spring", "Uploads and Scheduling", 14, "Advanced", "Multipart files, size limits and @Scheduled jobs.", ["Save an upload", "Cap file size", "Run a cron method"]),
    M("spring-events-messaging", "spring", "Domain Events and Messaging", 16, "Advanced", "Application events in-process and a first look at a message broker.", ["Publish an event", "Listen @TransactionalEventListener", "Sketch a queue"]),
    M("spring-testcontainers", "spring", "Tests with Testcontainers", 16, "Advanced", "Slice tests, MockMvc and a real Postgres in Docker for integration tests.", ["Write a @WebMvcTest", "Start Postgres in a test", "Replace a bean"]),
    M("spring-docker-deploy", "spring", "Docker, Profiles and Release", 16, "Advanced", "Layered jars, 12-factor config, graceful shutdown and health for orchestrators.", ["Build an image", "Use profiles", "Shut down cleanly"]),
]

CONTENT = {}

CONTENT["spring-security-jwt"] = [
    ("p", "<strong>Spring Security</strong> is a filter chain: every request is authenticated and then authorised. For a JSON API, disable sessions and accept a Bearer JWT."),
    ("h2", "The filter chain"),
    ("code", "java", '@Configuration\n@EnableWebSecurity\npublic class SecurityConfig {\n    @Bean\n    SecurityFilterChain api(HttpSecurity http, JwtAuthFilter jwt) throws Exception {\n        return http\n            .csrf(csrf -> csrf.disable())\n            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))\n            .authorizeHttpRequests(auth -> auth\n                .requestMatchers("/api/auth/**", "/actuator/health").permitAll()\n                .anyRequest().authenticated())\n            .addFilterBefore(jwt, UsernamePasswordAuthenticationFilter.class)\n            .build();\n    }\n\n    @Bean\n    PasswordEncoder passwordEncoder() {\n        return new BCryptPasswordEncoder();\n    }\n}'),
    ("h2", "Register and login"),
    ("code", "java", '@PostMapping("/api/auth/register")\npublic ResponseEntity<Void> register(@Valid @RequestBody RegisterRequest body) {\n    if (users.existsByEmail(body.email())) return ResponseEntity.status(409).build();\n    users.save(new User(body.email(), encoder.encode(body.password())));\n    return ResponseEntity.status(201).build();\n}\n\n@PostMapping("/api/auth/login")\npublic TokenResponse login(@RequestBody LoginRequest body) {\n    User user = users.findByEmail(body.email()).orElseThrow(() -> new BadCredentialsException("bad"));\n    if (!encoder.matches(body.password(), user.getPasswordHash())) throw new BadCredentialsException("bad");\n    return new TokenResponse(jwt.issue(user.getId()));\n}'),
    ("h2", "The JWT filter"),
    ("p", "Read <code>Authorization</code>, verify the signature, and set <code>SecurityContextHolder</code>. Skip the filter when the header is missing so public routes still work."),
    ("note", "Never log the token", "Treat JWTs like passwords. Keep <code>exp</code> short and put a secret (or a private key) in the environment."),
    ("exercise", "Permit <code>POST /api/auth/login</code> and require authentication for <code>GET /api/me</code>. Return 401 when the Bearer token is missing."),
]

CONTENT["spring-validation-errors"] = [
    ("p", "Bean Validation on the DTO plus a <code>@ControllerAdvice</code> that returns <code>ProblemDetail</code> gives clients a consistent error shape."),
    ("h2", "The DTO"),
    ("code", "java", 'public record CreateTaskRequest(\n    @NotBlank @Size(max = 100) String title,\n    @NotNull Boolean done\n) {}'),
    ("h2", "Problem details"),
    ("code", "java", '@RestControllerAdvice\npublic class ApiErrors {\n    @ExceptionHandler(MethodArgumentNotValidException.class)\n    ProblemDetail validation(MethodArgumentNotValidException ex) {\n        ProblemDetail pd = ProblemDetail.forStatus(HttpStatus.BAD_REQUEST);\n        pd.setTitle("Validation failed");\n        pd.setProperty("errors", ex.getBindingResult().getFieldErrors().stream()\n            .map(fe -> Map.of("field", fe.getField(), "message", fe.getDefaultMessage()))\n            .toList());\n        return pd;\n    }\n\n    @ExceptionHandler(NoSuchElementException.class)\n    ProblemDetail missing(NoSuchElementException ex) {\n        return ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());\n    }\n}'),
    ("p", "Return 422 only if you distinguish \"malformed JSON\" (400) from \"semantically invalid\" (422). Either way, be consistent."),
    ("exercise", "Reject a blank title with 400 and a missing task id with 404, both as <code>ProblemDetail</code>."),
]

CONTENT["spring-transactions"] = [
    ("p", "<code>@Transactional</code> wraps a method in a database transaction. It only works when called through the Spring proxy, on a public method, from another bean."),
    ("h2", "Where it belongs"),
    ("code", "java", '@Service\npublic class TransferService {\n    private final AccountRepository accounts;\n\n    @Transactional\n    public void transfer(long fromId, long toId, long cents) {\n        Account from = accounts.findByIdForUpdate(fromId).orElseThrow();\n        Account to = accounts.findByIdForUpdate(toId).orElseThrow();\n        from.debit(cents);\n        to.credit(cents);\n    }\n}'),
    ("p", "Keep transactions on the service layer, not on controllers, and as short as possible. Do not call HTTP inside one."),
    ("h2", "Optimistic locking"),
    ("code", "java", '@Entity\npublic class Product {\n    @Id @GeneratedValue Long id;\n    long stock;\n    @Version long version;\n}'),
    ("p", "A stale update throws <code>OptimisticLockException</code>. Catch it and retry, or tell the user to refresh."),
    ("note", "Self-invocation", "Calling <code>this.transfer(...)</code> from another method on the same class skips the proxy. Inject self, or move the method to another bean."),
    ("exercise", "Mark a service method transactional and add <code>@Version</code> to an entity that two users might edit at once."),
]

CONTENT["spring-caching"] = [
    ("p", "Spring Cache is a set of annotations over a cache manager. Start in-memory, switch to Redis when you have more than one instance."),
    ("h2", "Annotations"),
    ("code", "java", '@Configuration\n@EnableCaching\npublic class CacheConfig {}\n\n@Service\npublic class ProductService {\n    @Cacheable("products")\n    public ProductDto get(long id) { return repo.findById(id).map(this::toDto).orElseThrow(); }\n\n    @CacheEvict(value = "products", key = "#id")\n    public void rename(long id, String name) { ... }\n}'),
    ("h2", "Redis"),
    ("code", "java", '@Bean\npublic RedisCacheManager cacheManager(RedisConnectionFactory f) {\n    RedisCacheConfiguration cfg = RedisCacheConfiguration.defaultCacheConfig()\n        .entryTtl(Duration.ofMinutes(5));\n    return RedisCacheManager.builder(f).cacheDefaults(cfg).build();\n}'),
    ("p", "Cache keys must include everything that changes the result (id, locale, tenant). Evict on every write path, including deletes."),
    ("exercise", "Cache <code>get(id)</code> for 5 minutes and evict that key from <code>update</code> and <code>delete</code>."),
]

CONTENT["spring-actuator"] = [
    ("p", "<strong>Actuator</strong> exposes operational endpoints: health for the load balancer, metrics for Prometheus, info for the build version."),
    ("h2", "Dependencies and exposure"),
    ("code", "yaml", '# application.yml\nmanagement:\n  endpoints:\n    web:\n      exposure:\n        include: health,info,prometheus\n  endpoint:\n    health:\n      show-details: when_authorized\n      probes:\n        enabled: true          # /actuator/health/liveness and /readiness'),
    ("h2", "A custom health indicator"),
    ("code", "java", '@Component\npublic class DiskHealth implements HealthIndicator {\n    @Override public Health health() {\n        long free = new File("/").getUsableSpace();\n        return free < 100_000_000\n            ? Health.down().withDetail("free", free).build()\n            : Health.up().build();\n    }\n}'),
    ("p", "Do not expose <code>env</code> or <code>heapdump</code> on the public internet. Put Actuator on a separate port or restrict it to the cluster network."),
    ("exercise", "Expose only <code>health</code> and <code>prometheus</code>, and add a health indicator that is <code>DOWN</code> when a required directory is missing."),
]

CONTENT["spring-openapi"] = [
    ("p", "<strong>springdoc-openapi</strong> reads your controllers and produces Swagger UI at <code>/swagger-ui.html</code>."),
    ("h2", "Setup"),
    ("code", "text", "implementation 'org.springdoc:springdoc-openapi-starter-webmvc-ui:2.6.0'"),
    ("code", "java", '@OpenAPIDefinition(info = @Info(title = "Tasks API", version = "1.0"))\n@SecurityScheme(name = "bearer", type = SecuritySchemeType.HTTP, scheme = "bearer", bearerFormat = "JWT")\n@RestController\nclass TaskController {\n    @Operation(summary = "List tasks")\n    @SecurityRequirement(name = "bearer")\n    @GetMapping("/api/tasks")\n    List<TaskDto> list() { ... }\n}'),
    ("p", "Records used as request bodies show up as schemas automatically. Hide internal endpoints with <code>@Hidden</code>."),
    ("exercise", "Add springdoc, set the API title, and require a Bearer scheme on a protected controller method."),
]

CONTENT["spring-files-scheduling"] = [
    ("p", "Two small but common features: receiving a file and running a method on a schedule."),
    ("h2", "Multipart"),
    ("code", "java", '@PostMapping(value = "/api/files", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)\npublic Map<String, String> upload(@RequestParam("file") MultipartFile file) throws IOException {\n    if (file.isEmpty()) throw new ResponseStatusException(HttpStatus.BAD_REQUEST);\n    String name = UUID.randomUUID() + "-" + file.getOriginalFilename();\n    Path dest = Path.of(uploadDir, name);\n    file.transferTo(dest);\n    return Map.of("name", name);\n}'),
    ("code", "yaml", 'spring:\n  servlet:\n    multipart:\n      max-file-size: 5MB\n      max-request-size: 5MB'),
    ("h2", "Scheduling"),
    ("code", "java", '@Configuration\n@EnableScheduling\npublic class ScheduleConfig {}\n\n@Component\npublic class PurgeJob {\n    @Scheduled(cron = "0 15 3 * * *")   // 03:15 every day\n    public void purgeExpired() { ... }\n}'),
    ("note", "One instance", "Every replica runs <code>@Scheduled</code>. Use a ShedLock (or a real job runner) if the work must run once cluster-wide."),
    ("exercise", "Reject empty uploads and add a scheduled method that logs a heartbeat every 60 seconds (<code>fixedRate</code>)."),
]

CONTENT["spring-events-messaging"] = [
    ("p", "Decouple \"order placed\" from \"send email\" with events. Start in-process; move to a broker when another service must consume the same fact."),
    ("h2", "Application events"),
    ("code", "java", 'public record OrderPlaced(long orderId, String email) {}\n\n@Service\npublic class CheckoutService {\n    private final ApplicationEventPublisher events;\n    @Transactional\n    public void checkout(Cart cart) {\n        Order order = orders.save(...);\n        events.publishEvent(new OrderPlaced(order.getId(), cart.getEmail()));\n    }\n}\n\n@Component\npublic class MailListener {\n    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)\n    public void on(OrderPlaced event) {\n        mail.sendReceipt(event.email(), event.orderId());\n    }\n}'),
    ("p", "<code>AFTER_COMMIT</code> avoids sending mail for a rolled-back order. Listeners in the same JVM still fail silently if the process dies; a queue (RabbitMQ, SQS, Kafka) is the next step."),
    ("h2", "When to use a broker"),
    ("ul", [
        "Another service needs the event.",
        "Work must retry independently of the web node.",
        "You need a durable audit of what happened.",
    ]),
    ("exercise", "Publish an event after creating a user and send a welcome email only after the transaction commits."),
]

CONTENT["spring-testcontainers"] = [
    ("p", "Slice tests are fast. Integration tests against a real Postgres in Docker catch the SQL the H2 database hides."),
    ("h2", "WebMvcTest"),
    ("code", "java", '@WebMvcTest(TaskController.class)\nclass TaskControllerTest {\n    @Autowired MockMvc mvc;\n    @MockBean TaskService tasks;\n\n    @Test\n    void listsTasks() throws Exception {\n        when(tasks.list()).thenReturn(List.of(new TaskDto(1L, "Hi", false)));\n        mvc.perform(get("/api/tasks"))\n            .andExpect(status().isOk())\n            .andExpect(jsonPath("$[0].title").value("Hi"));\n    }\n}'),
    ("h2", "Testcontainers"),
    ("code", "java", '@SpringBootTest\n@Testcontainers\nclass TaskRepoIT {\n    @Container\n    static PostgreSQLContainer<?> pg = new PostgreSQLContainer<>("postgres:16-alpine");\n\n    @DynamicPropertySource\n    static void props(DynamicPropertyRegistry r) {\n        r.add("spring.datasource.url", pg::getJdbcUrl);\n        r.add("spring.datasource.username", pg::getUsername);\n        r.add("spring.datasource.password", pg::getPassword);\n    }\n}'),
    ("note", "CI", "GitHub Actions and most CI images can run Docker. If not, skip the test with <code>@EnabledIfEnvironmentVariable</code>."),
    ("exercise", "Write a <code>@WebMvcTest</code> that stubs the service and expects 404 JSON when it throws <code>NoSuchElementException</code>."),
]

CONTENT["spring-docker-deploy"] = [
    ("p", "Spring Boot 3 builds a layered jar that Docker can cache. Config stays in the environment; the process shuts down on SIGTERM."),
    ("h2", "Image"),
    ("code", "dockerfile", 'FROM eclipse-temurin:21-jre\nWORKDIR /app\nCOPY build/libs/app.jar app.jar\nEXPOSE 8080\nENTRYPOINT ["java","-XX:MaxRAMPercentage=75","-jar","app.jar"]'),
    ("h2", "Profiles and shutdown"),
    ("code", "yaml", 'spring:\n  profiles:\n    active: ${APP_ENV:prod}\n  lifecycle:\n    timeout-per-shutdown-phase: 20s\nserver:\n  shutdown: graceful'),
    ("p", "The load balancer should call <code>/actuator/health/readiness</code>. On SIGTERM, Boot stops taking new work, waits in-flight requests, then exits."),
    ("ul", [
        "Secrets and URLs from env, not <code>application.yml</code> committed to git.",
        "Flyway/Liquibase migrate on startup or as a release job.",
        "Pin the Java and base image versions.",
    ]),
    ("exercise", "Enable graceful shutdown and point readiness at Actuator so Kubernetes (or your host) can drain the instance."),
]
