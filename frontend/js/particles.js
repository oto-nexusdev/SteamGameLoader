// frontend/js/particles.js
class ParticleSystem {
    constructor() {
        this.canvas = document.getElementById('particlesCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.particles = [];
        this.mouse = { x: 0, y: 0, radius: 150 };
        this.animationId = null;
        
        // Novos parâmetros para gravidade
        this.gravityStrength = 0.05;
        this.maxGravityDistance = 100;
        
        this.init();
    }

    init() {
        this.resizeCanvas();
        this.createParticles();
        this.bindEvents();
        this.animate();
    }

    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticles() {
        const particleCount = Math.min(150, Math.floor((window.innerWidth * window.innerHeight) / 8000));
        
        for (let i = 0; i < particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                size: Math.random() * 2 + 0.5,
                speedX: (Math.random() - 0.5) * 0.3, // Reduzido para mais suavidade
                speedY: (Math.random() - 0.5) * 0.3,
                color: this.getRandomParticleColor(),
                opacity: Math.random() * 0.6 + 0.2,
                mass: Math.random() * 1.5 + 0.5 // Massa para gravidade
            });
        }
    }

    getRandomParticleColor() {
        const colors = [
            'rgba(122, 42, 255, OPACITY)',    // Neon Purple
            'rgba(77, 224, 255, OPACITY)',    // Neon Cyan
            'rgba(255, 42, 109, OPACITY)',    // Neon Pink
            'rgba(0, 230, 118, OPACITY)',     // Success Green
            'rgba(102, 192, 244, OPACITY)'    // Steam Blue
        ];
        const color = colors[Math.floor(Math.random() * colors.length)];
        return color.replace('OPACITY', '0.8');
    }

    bindEvents() {
        window.addEventListener('resize', () => {
            this.resizeCanvas();
        });

        window.addEventListener('mousemove', (e) => {
            this.mouse.x = e.clientX;
            this.mouse.y = e.clientY;
        });

        window.addEventListener('mouseleave', () => {
            this.mouse.x = -100;
            this.mouse.y = -100;
        });
    }

    applyGravity() {
        // Aplicar gravidade entre todas as partículas
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const p1 = this.particles[i];
                const p2 = this.particles[j];
                
                const dx = p2.x - p1.x;
                const dy = p2.y - p1.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                // Aplicar gravidade apenas se dentro do raio máximo
                if (distance > 0 && distance < this.maxGravityDistance) {
                    const force = this.gravityStrength * (p1.mass * p2.mass) / (distance * distance);
                    const angle = Math.atan2(dy, dx);
                    
                    // Aplicar força proporcional à massa
                    const forceX = Math.cos(angle) * force;
                    const forceY = Math.sin(angle) * force;
                    
                    p1.speedX += forceX / p1.mass;
                    p1.speedY += forceY / p1.mass;
                    p2.speedX -= forceX / p2.mass;
                    p2.speedY -= forceY / p2.mass;
                }
            }
        }
    }

    drawParticles() {
        // Aplicar gravidade entre partículas
        this.applyGravity();

        this.particles.forEach(particle => {
            // Efeito de atração gravitacional com o mouse
            const dx = this.mouse.x - particle.x;
            const dy = this.mouse.y - particle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < this.mouse.radius) {
                const force = (this.mouse.radius - distance) / this.mouse.radius;
                const angle = Math.atan2(dy, dx);
                
                // Força mais suave do mouse
                particle.speedX += Math.cos(angle) * force * 0.05;
                particle.speedY += Math.sin(angle) * force * 0.05;
                
                // Efeito de brilho quando próximo ao mouse
                particle.opacity = Math.min(1, particle.opacity + force * 0.2);
            } else {
                // Retorno suave à opacidade original
                particle.opacity = Math.max(0.2, particle.opacity - 0.01);
            }

            // Atualizar posição com amortecimento
            particle.x += particle.speedX;
            particle.y += particle.speedY;

            // Rebater nas bordas de forma mais suave
            if (particle.x <= 0 || particle.x >= this.canvas.width) {
                particle.speedX *= -0.9;
                particle.x = Math.max(0, Math.min(this.canvas.width, particle.x));
            }
            if (particle.y <= 0 || particle.y >= this.canvas.height) {
                particle.speedY *= -0.9;
                particle.y = Math.max(0, Math.min(this.canvas.height, particle.y));
            }

            // Amortecimento mais forte para movimento mais suave
            particle.speedX *= 0.97;
            particle.speedY *= 0.97;

            // Limitar velocidade máxima para suavidade
            const maxSpeed = 2;
            const currentSpeed = Math.sqrt(particle.speedX * particle.speedX + particle.speedY * particle.speedY);
            if (currentSpeed > maxSpeed) {
                particle.speedX = (particle.speedX / currentSpeed) * maxSpeed;
                particle.speedY = (particle.speedY / currentSpeed) * maxSpeed;
            }

            // Desenhar partícula com sombra sutil
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            
            // Efeito de glow suave
            this.ctx.shadowBlur = 15;
            this.ctx.shadowColor = particle.color.replace('0.8', '0.6');
            this.ctx.fillStyle = particle.color.replace('0.8', particle.opacity.toString());
            this.ctx.fill();
            
            // Resetar shadow para as conexões
            this.ctx.shadowBlur = 0;
        });

        this.drawConnections();
    }

    drawConnections() {
        for (let i = 0; i < this.particles.length; i++) {
            for (let j = i + 1; j < this.particles.length; j++) {
                const dx = this.particles[i].x - this.particles[j].x;
                const dy = this.particles[i].y - this.particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 120) {
                    const opacity = 1 - (distance / 120);
                    this.ctx.beginPath();
                    this.ctx.strokeStyle = `rgba(122, 42, 255, ${opacity * 0.2})`;
                    this.ctx.lineWidth = 0.5;
                    this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                    this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                    this.ctx.stroke();
                }
            }
        }
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Fundo gradiente mais sutil
        const gradient = this.ctx.createRadialGradient(
            this.canvas.width / 2,
            this.canvas.height / 2,
            0,
            this.canvas.width / 2,
            this.canvas.height / 2,
            Math.max(this.canvas.width, this.canvas.height) / 2
        );
        gradient.addColorStop(0, 'rgba(10, 8, 20, 0.05)');
        gradient.addColorStop(1, 'rgba(4, 2, 8, 0.1)');
        
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.drawParticles();
        this.animationId = requestAnimationFrame(() => this.animate());
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        window.particleSystem = new ParticleSystem();
    }, 1000);
});

// Exportar para uso global
window.ParticleSystem = ParticleSystem;