import { AsyncResponseManager } from '../core/AsyncResponseManager';
import { ApiResponse, RequestConfig } from '../types/response.types';

export class UserService {
  private manager = AsyncResponseManager.getInstance();

  async getUsers(): Promise<ApiResponse> {
    return this.manager.request({
      url: 'https://jsonplaceholder.typicode.com/users',
      method: 'GET'
    }, {
      showNotification: true,
      persistResult: true,
      context: { service: 'UserService', operation: 'getUsers' }
    });
  }

  async getUser(id: number): Promise<ApiResponse> {
    return this.manager.request({
      url: `https://jsonplaceholder.typicode.com/users/${id}`,
      method: 'GET'
    }, {
      showNotification: false,
      persistResult: true,
      context: { service: 'UserService', operation: 'getUser', userId: id }
    });
  }

  async createUser(userData: any): Promise<ApiResponse> {
    return this.manager.request({
      url: 'https://jsonplaceholder.typicode.com/users',
      method: 'POST',
      data: userData
    }, {
      showNotification: true,
      persistResult: true,
      context: { service: 'UserService', operation: 'createUser' }
    });
  }

  async updateUser(id: number, userData: any): Promise<ApiResponse> {
    return this.manager.request({
      url: `https://jsonplaceholder.typicode.com/users/${id}`,
      method: 'PUT',
      data: userData
    }, {
      showNotification: true,
      context: { service: 'UserService', operation: 'updateUser', userId: id }
    });
  }

  async deleteUser(id: number): Promise<ApiResponse> {
    return this.manager.request({
      url: `https://jsonplaceholder.typicode.com/users/${id}`,
      method: 'DELETE'
    }, {
      showNotification: true,
      context: { service: 'UserService', operation: 'deleteUser', userId: id }
    });
  }
}

export class PostService {
  private manager = AsyncResponseManager.getInstance();

  async getPosts(): Promise<ApiResponse> {
    return this.manager.request({
      url: 'https://jsonplaceholder.typicode.com/posts',
      method: 'GET'
    }, {
      showNotification: false,
      persistResult: true,
      context: { service: 'PostService', operation: 'getPosts' }
    });
  }

  async getPost(id: number): Promise<ApiResponse> {
    return this.manager.request({
      url: `https://jsonplaceholder.typicode.com/posts/${id}`,
      method: 'GET'
    }, {
      showNotification: false,
      persistResult: true,
      context: { service: 'PostService', operation: 'getPost', postId: id }
    });
  }

  async getUserPosts(userId: number): Promise<ApiResponse> {
    return this.manager.request({
      url: `https://jsonplaceholder.typicode.com/posts?userId=${userId}`,
      method: 'GET'
    }, {
      showNotification: false,
      context: { service: 'PostService', operation: 'getUserPosts', userId }
    });
  }

  async createPost(postData: any): Promise<ApiResponse> {
    return this.manager.request({
      url: 'https://jsonplaceholder.typicode.com/posts',
      method: 'POST',
      data: postData
    }, {
      showNotification: true,
      context: { service: 'PostService', operation: 'createPost' }
    });
  }

  async updatePost(id: number, postData: any): Promise<ApiResponse> {
    return this.manager.request({
      url: `https://jsonplaceholder.typicode.com/posts/${id}`,
      method: 'PUT',
      data: postData
    }, {
      showNotification: true,
      context: { service: 'PostService', operation: 'updatePost', postId: id }
    });
  }

  async deletePost(id: number): Promise<ApiResponse> {
    return this.manager.request({
      url: `https://jsonplaceholder.typicode.com/posts/${id}`,
      method: 'DELETE'
    }, {
      showNotification: true,
      context: { service: 'PostService', operation: 'deletePost', postId: id }
    });
  }
}

export class CommentService {
  private manager = AsyncResponseManager.getInstance();

  async getComments(): Promise<ApiResponse> {
    return this.manager.request({
      url: 'https://jsonplaceholder.typicode.com/comments',
      method: 'GET'
    }, {
      showNotification: false,
      context: { service: 'CommentService', operation: 'getComments' }
    });
  }

  async getPostComments(postId: number): Promise<ApiResponse> {
    return this.manager.request({
      url: `https://jsonplaceholder.typicode.com/comments?postId=${postId}`,
      method: 'GET'
    }, {
      showNotification: false,
      context: { service: 'CommentService', operation: 'getPostComments', postId }
    });
  }

  async createComment(commentData: any): Promise<ApiResponse> {
    return this.manager.request({
      url: 'https://jsonplaceholder.typicode.com/comments',
      method: 'POST',
      data: commentData
    }, {
      showNotification: true,
      context: { service: 'CommentService', operation: 'createComment' }
    });
  }
}

export class DataAggregationService {
  private userService = new UserService();
  private postService = new PostService();
  private commentService = new CommentService();
  private manager = AsyncResponseManager.getInstance();
  private transactionManager = this.manager.flows;

  /**
   * Ejemplo de servicio complejo que obtiene datos agregados
   */
  async getDashboardData(): Promise<ApiResponse> {
    return this.transactionManager.executeFlow({
      id: `dashboard_${Date.now()}`,
      name: 'Cargar Dashboard',
      steps: [
        {
          id: 'load_users',
          name: 'Cargar Usuarios',
          action: async () => {
            const response = await this.userService.getUsers();
            if (!response.success) throw new Error('Error cargando usuarios');
            return response.data;
          }
        },
        {
          id: 'load_posts',
          name: 'Cargar Posts',
          action: async () => {
            const response = await this.postService.getPosts();
            if (!response.success) throw new Error('Error cargando posts');
            return response.data;
          },
          dependencies: ['load_users']
        },
        {
          id: 'load_comments',
          name: 'Cargar Comentarios',
          action: async () => {
            const response = await this.commentService.getComments();
            if (!response.success) throw new Error('Error cargando comentarios');
            return response.data;
          },
          dependencies: ['load_users']
        },
        {
          id: 'aggregate_data',
          name: 'Agregar Datos',
          action: async (results: any) => {
            const users = results.load_users;
            const posts = results.load_posts;
            const comments = results.load_comments;

            // Procesar datos agregados
            const dashboardData = {
              usersCount: users?.length || 0,
              postsCount: posts?.length || 0,
              commentsCount: comments?.length || 0,
              recentUsers: users?.slice(0, 5) || [],
              recentPosts: posts?.slice(0, 5) || [],
              topCommenters: this.calculateTopCommenters(comments || []),
              postStats: this.calculatePostStats(posts || [])
            };

            return dashboardData;
          },
          dependencies: ['load_users', 'load_posts', 'load_comments']
        }
      ],
      currentStep: 0,
      status: 'pending',
      createdAt: Date.now(),
      updatedAt: Date.now()
    }, {
      showProgress: true
    });
  }

  /**
   * Ejemplo de flujo de creación completa (usuario + post + comentarios)
   */
  async createUserWithPosts(userData: any, postsData: any[]): Promise<ApiResponse> {
    return this.transactionManager.executeFlow({
      id: `create_user_complete_${Date.now()}`,
      name: 'Crear Usuario Completo',
      steps: [
        {
          id: 'create_user',
          name: 'Crear Usuario',
          action: async () => {
            const response = await this.userService.createUser(userData);
            if (!response.success) throw new Error('Error creando usuario');
            return response.data;
          },
          rollback: async () => {
            // Rollback: eliminar usuario si falla algo después
            console.log('Rollback: Eliminando usuario creado');
          }
        },
        {
          id: 'create_posts',
          name: 'Crear Posts',
          action: async (results: any) => {
            const user = results.create_user;
            const createdPosts = [];

            for (const postData of postsData) {
              const postWithUser = { ...postData, userId: user.id };
              const response = await this.postService.createPost(postWithUser);
              if (!response.success) throw new Error(`Error creando post`);
              createdPosts.push(response.data);
            }

            return createdPosts;
          },
          rollback: async (results: any) => {
            // Rollback: eliminar posts creados
            if (results.create_posts) {
              for (const post of results.create_posts) {
                await this.postService.deletePost(post.id);
              }
            }
          },
          dependencies: ['create_user']
        },
        {
          id: 'add_initial_comments',
          name: 'Agregar Comentarios Iniciales',
          action: async (results: any) => {
            const user = results.create_user;
            const posts = results.create_posts;
            const comments = [];

            // Agregar un comentario de bienvenida a cada post
            for (const post of posts) {
              const welcomeComment = {
                postId: post.id,
                name: 'Sistema',
                email: 'sistema@example.com',
                body: `¡Bienvenido al sistema, ${user.name}! 🎉`
              };

              const response = await this.commentService.createComment(welcomeComment);
              if (response.success) {
                comments.push(response.data);
              }
            }

            return comments;
          },
          rollback: async (results: any) => {
            // Rollback: eliminar comentarios creados
            if (results.add_initial_comments) {
              for (const comment of results.add_initial_comments) {
                // Aquí necesitarías un método deleteComment
                console.log(`Rollback: Eliminando comentario ${comment.id}`);
              }
            }
          },
          dependencies: ['create_posts']
        },
        {
          id: 'finalize',
          name: 'Finalizar',
          action: async (results: any) => {
            return {
              user: results.create_user,
              posts: results.create_posts,
              comments: results.add_initial_comments,
              message: 'Usuario creado exitosamente con posts y comentarios'
            };
          },
          dependencies: ['add_initial_comments']
        }
      ],
      currentStep: 0,
      status: 'pending',
      createdAt: Date.now(),
      updatedAt: Date.now()
    }, {
      showProgress: true
    });
  }

  private calculateTopCommenters(comments: any[]): any[] {
    const commenterCounts = comments.reduce((acc, comment) => {
      acc[comment.email] = (acc[comment.email] || 0) + 1;
      return acc;
    }, {});

    return Object.entries(commenterCounts)
      .map(([email, count]) => ({ email, commentCount: count }))
      .sort((a, b) => b.commentCount - a.commentCount)
      .slice(0, 5);
  }

  private calculatePostStats(posts: any[]): any {
    const totalLength = posts.reduce((sum, post) => sum + (post.body?.length || 0), 0);
    const averageLength = posts.length > 0 ? totalLength / posts.length : 0;

    return {
      totalPosts: posts.length,
      averageLength: Math.round(averageLength),
      totalCharacters: totalLength
    };
  }
}

// Instancias singleton para uso en la aplicación
export const userService = new UserService();
export const postService = new PostService();
export const commentService = new CommentService();
export const dataAggregationService = new DataAggregationService();