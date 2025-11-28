import { Component, OnInit, AfterViewInit, OnDestroy, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ProductCardComponent } from '../../shared/product-card/product-card.component';
import { ProductoService } from '../../../services/tienda/producto.service';
import { Producto } from '../../../models/producto';
import { environment } from '../../../../environments/environment';

declare var bootstrap: any;

@Component({
  selector: 'app-tienda',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, ProductCardComponent],
  templateUrl: './tienda.html',
  styleUrls: ['./tienda.css', './pagination.css']
})
export class TiendaComponent implements OnInit, AfterViewInit, OnDestroy {

  // Datos de productos de la API
  productos: Producto[] = [];

  // Filtros
  categoriaSeleccionada: string = 'Todos';
  categorias = ['Todos', 'Disponibles', 'No Disponibles'];
  
  // Filtros por tipo de producto
  tipoProductoSeleccionado: string = 'Todos los productos';
  tiposProducto = ['Todos los productos', 'Taco', 'Postre', 'Acompañamiento', 'Bebida'];
  
  // Búsqueda de texto
  textoBusqueda: string = '';

  // Productos filtrados
  productosFiltrados: Producto[] = [];
  isLoading = true;
  error: string | null = null;

  // Paginación nativa
  paginaActual: number = 1;
  productosPorPagina: number = 9;
  totalPaginas: number = 0;
  productosPaginados: Producto[] = [];

  // Estado del usuario (simulado por ahora)
  loggedUser: any = null; // Aquí integrarás con tu servicio de autenticación

  // Estado del chatbot flotante
  showChatbot = false;
  chatbotUrl: SafeResourceUrl;

  // Mantener referencia al observer para poder desconectarlo
  private scrollObserver: IntersectionObserver | null = null;

  constructor(
    private productoService: ProductoService,
    private router: Router,
    private elementRef: ElementRef,
    private sanitizer: DomSanitizer
  ) {
    this.chatbotUrl = this.sanitizer.bypassSecurityTrustResourceUrl(environment.chatbotUserUrl);
  }

  ngOnInit(): void {
    this.cargarProductos();
    
    // Agregar clase al body para habilitar animaciones solo si JS está funcionando
    document.documentElement.classList.add('js-enabled');
  }

  ngAfterViewInit(): void {
    // Inicializar componentes Bootstrap
    this.initializeBootstrapComponents();

    // Esperar a que los productos se carguen antes de inicializar animaciones
    setTimeout(() => {
      this.setupScrollAnimations();
    }, 100);
  }

  ngOnDestroy(): void {
    // Limpiar el observer para evitar memory leaks
    if (this.scrollObserver) {
      this.scrollObserver.disconnect();
      this.scrollObserver = null;
    }
    
    // Remover clase del documento
    document.documentElement.classList.remove('js-enabled');
  }

  private initializeBootstrapComponents(): void {
    // Inicializar tooltips
    const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(tooltipTriggerEl => {
      new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }

  private setupScrollAnimations(): void {
    // Desconectar observer anterior si existe
    if (this.scrollObserver) {
      this.scrollObserver.disconnect();
    }

    const revealElements = this.elementRef.nativeElement.querySelectorAll('.scroll-reveal');

    if (revealElements.length === 0) {
      console.log('No hay elementos con scroll-reveal para animar');
      return;
    }

    console.log(`Configurando animaciones para ${revealElements.length} elementos`);

    // Fallback: Si IntersectionObserver no está disponible, mostrar todo inmediatamente
    if (!('IntersectionObserver' in window)) {
      console.warn('IntersectionObserver no disponible, mostrando todas las cards');
      revealElements.forEach((element: Element) => {
        (element as HTMLElement).style.opacity = '1';
        (element as HTMLElement).style.transform = 'translateY(0)';
      });
      return;
    }

    this.scrollObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry: IntersectionObserverEntry, index: number) => {
        if (entry.isIntersecting) {
          const element = entry.target as HTMLElement;
          const animation = element.dataset['animation'] || 'animate__fadeInUp';

          // Añadir animación más rápida
          setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
            element.classList.add('animate__animated', animation, 'animate__faster');
          }, index * 30); // Delay más corto entre elementos

          this.scrollObserver?.unobserve(element);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '50px' // Empezar la animación antes de que el elemento sea visible
    });

    revealElements.forEach((element: Element) => {
      this.scrollObserver?.observe(element);
    });

    // Timeout de seguridad: Si después de 2 segundos hay elementos invisibles, mostrarlos
    setTimeout(() => {
      revealElements.forEach((element: Element) => {
        const htmlElement = element as HTMLElement;
        if (htmlElement.style.opacity === '0' || !htmlElement.style.opacity) {
          console.warn('Elemento todavía invisible, forzando visibilidad:', element);
          htmlElement.style.opacity = '1';
          htmlElement.style.transform = 'translateY(0)';
        }
      });
    }, 2000);
  }

  private mostrarTodosLosProductos(): void {
    const revealElements = this.elementRef.nativeElement.querySelectorAll('.scroll-reveal');
    revealElements.forEach((element: Element) => {
      const htmlElement = element as HTMLElement;
      const computedStyle = window.getComputedStyle(htmlElement);
      
      // Si el elemento está invisible o con opacidad muy baja
      if (parseFloat(computedStyle.opacity) < 0.5) {
        console.warn('Forzando visibilidad de producto después del timeout final:', element);
        htmlElement.style.opacity = '1';
        htmlElement.style.transform = 'translateY(0)';
        htmlElement.classList.add('animate__animated', 'animate__fadeIn', 'animate__faster');
      }
    });
  }

  private cargarProductos(): void {
    this.isLoading = true;
    this.error = null;

    console.log('Intentando cargar productos desde:', this.productoService);

    this.productoService.getProductosActivos().subscribe({
      next: (productos) => {
        console.log('✅ Productos cargados exitosamente:', productos);
        console.log('Total de productos recibidos:', productos?.length || 0);
        
        this.productos = productos || [];
        this.filtrarProductos();
        this.isLoading = false;
        
        if (this.productos.length === 0) {
          console.warn('⚠️ No se encontraron productos en la respuesta');
        }
      },
      error: (error) => {
        console.error('❌ Error detallado al cargar productos:', error);
        console.error('Status:', error.status);
        console.error('Message:', error.message);
        console.error('URL:', error.url);
        
        if (error.status === 0) {
          this.error = '❌ No se puede conectar al servidor. Verifica que el backend esté corriendo en http://localhost:9998';
        } else if (error.status === 404) {
          this.error = '❌ Endpoint no encontrado. Verifica la ruta de la API.';
        } else if (error.status === 500) {
          this.error = '❌ Error en el servidor. Revisa los logs del backend.';
        } else {
          this.error = `❌ Error al cargar los productos: ${error.message}`;
        }
        
        this.isLoading = false;
        this.productos = [];
        this.productosFiltrados = [];
      }
    });
  }

  // Métodos de filtrado
  filtrarPorCategoria(categoria: string): void {
    this.categoriaSeleccionada = categoria;
    this.paginaActual = 1; // Resetear a la primera página al cambiar filtro
    this.filtrarProductos();
  }
  
  filtrarPorTipoProducto(tipo: string): void {
    this.tipoProductoSeleccionado = tipo;
    this.paginaActual = 1;
    this.filtrarProductos();
  }
  
  buscarProductos(texto: string): void {
    this.textoBusqueda = texto;
    this.paginaActual = 1;
    this.filtrarProductos();
  }
  
  limpiarBusqueda(): void {
    this.textoBusqueda = '';
    this.filtrarProductos();
  }

  private filtrarProductos(): void {
    console.log('Filtrando por categoría:', this.categoriaSeleccionada);
    console.log('Productos base:', this.productos);

    // Primero, excluir productos personalizados de todos los resultados
    let productosBase = this.productos.filter(producto => 
      !producto.nombre?.toLowerCase().includes('personalizado')
    );

    // Filtrar por disponibilidad
    if (this.categoriaSeleccionada === 'Disponibles') {
      productosBase = productosBase.filter(producto =>
        producto.disponible === true || (producto.disponible as any) === 1
      );
    } else if (this.categoriaSeleccionada === 'No Disponibles') {
      productosBase = productosBase.filter(producto =>
        producto.disponible === false || (producto.disponible as any) === 0
      );
    }
    
    // Filtrar por tipo de producto (Taco, Postre, Acompañamiento, Bebida)
    if (this.tipoProductoSeleccionado !== 'Todos los productos') {
      productosBase = productosBase.filter(producto => {
        const categoriaProducto = producto.categoria?.toUpperCase() || '';
        const tipoLower = this.tipoProductoSeleccionado.toLowerCase();
        
        // Mapear el tipo seleccionado a la categoría en la BD
        let categoriaEsperada = '';
        if (tipoLower === 'taco') categoriaEsperada = 'TACO';
        else if (tipoLower === 'postre') categoriaEsperada = 'POSTRE';
        else if (tipoLower === 'acompañamiento') categoriaEsperada = 'ACOMPAÑAMIENTO';
        else if (tipoLower === 'bebida') categoriaEsperada = 'BEBIDA';
        
        return categoriaProducto === categoriaEsperada;
      });
    }
    
    // Filtrar por texto de búsqueda
    if (this.textoBusqueda && this.textoBusqueda.trim() !== '') {
      const busquedaLower = this.textoBusqueda.toLowerCase().trim();
      productosBase = productosBase.filter(producto => {
        const nombreLower = producto.nombre?.toLowerCase() || '';
        const descripcionLower = producto.descripcion?.toLowerCase() || '';
        
        return nombreLower.includes(busquedaLower) || descripcionLower.includes(busquedaLower);
      });
    }
    
    this.productosFiltrados = productosBase;

    console.log('Productos filtrados resultado:', this.productosFiltrados);
    
    // Actualizar paginación después de filtrar
    this.actualizarPaginacion();
  }

  // Métodos de paginación nativa
  private actualizarPaginacion(): void {
    this.totalPaginas = Math.ceil(this.productosFiltrados.length / this.productosPorPagina);
    this.cargarProductosPaginados();
  }

  private cargarProductosPaginados(): void {
    const inicio = (this.paginaActual - 1) * this.productosPorPagina;
    const fin = inicio + this.productosPorPagina;
    this.productosPaginados = this.productosFiltrados.slice(inicio, fin);
    
    // Reinicializar animaciones después de cambiar los productos
    // Usar múltiples intentos para asegurar que el DOM esté listo
    setTimeout(() => {
      this.setupScrollAnimations();
    }, 50);
    
    // Fallback adicional por si el primero falla
    setTimeout(() => {
      this.setupScrollAnimations();
    }, 200);
    
    // Fallback final: Mostrar todo si no se han animado después de 3 segundos
    setTimeout(() => {
      this.mostrarTodosLosProductos();
    }, 3000);
  }

  cambiarPagina(pagina: number): void {
    if (pagina >= 1 && pagina <= this.totalPaginas) {
      this.paginaActual = pagina;
      this.cargarProductosPaginados();
      
      // Scroll suave al inicio de los productos
      const productosSection = document.querySelector('.row.g-4');
      if (productosSection) {
        productosSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
  }

  paginaAnterior(): void {
    this.cambiarPagina(this.paginaActual - 1);
  }

  paginaSiguiente(): void {
    this.cambiarPagina(this.paginaActual + 1);
  }

  getPaginasArray(): number[] {
    const paginas: number[] = [];
    const maxPaginasVisibles = 5;
    
    let inicio = Math.max(1, this.paginaActual - Math.floor(maxPaginasVisibles / 2));
    let fin = Math.min(this.totalPaginas, inicio + maxPaginasVisibles - 1);
    
    if (fin - inicio < maxPaginasVisibles - 1) {
      inicio = Math.max(1, fin - maxPaginasVisibles + 1);
    }
    
    for (let i = inicio; i <= fin; i++) {
      paginas.push(i);
    }
    
    return paginas;
  }

  // Métodos helper para las estrellas
  getStarsArray(rating: number): number[] {
    return Array.from({ length: rating }, (_, i) => i);
  }

  getEmptyStarsArray(rating: number): number[] {
    return Array.from({ length: 5 - rating }, (_, i) => i);
  }

  // Navegación y acciones
  navigateToProduct(productId: number): void {
    console.log('Navegando a producto:', productId);
    this.router.navigate(['/producto', productId]).then(() => {
      window.scrollTo({ top: 0, left: 0, behavior: 'smooth' });
    });
  }

  agregarAlCarrito(producto: any): void {
    console.log('Agregando al carrito:', producto);
    // Aquí implementarás la lógica del carrito
  }

  crearTacoPersonalizado(): void {
    // Navegar al constructor de tacos personalizado
    this.router.navigate(['/crear-taco']).then(() => {
      window.scrollTo({ top: 0, left: 0, behavior: 'smooth' });
    });
  }

  toggleChatbot(): void {
    this.showChatbot = !this.showChatbot;
  }
}
