/**
 * API Client for Student Management System
 */

const API = {
    // Base helper for handling fetch requests
    async request(url, options = {}) {
        try {
            const config = {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            };
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                const message = data.detail || (Array.isArray(data) ? data[0]?.msg : 'Request failed');
                throw new Error(message);
            }
            return data;
        } catch (error) {
            console.error(`API Error [${url}]:`, error);
            throw error;
        }
    },

    // --- Students ---
    getStudents(params = {}) {
        const query = new URLSearchParams();
        if (params.search) query.append('search', params.search);
        if (params.department_id) query.append('department_id', params.department_id);
        if (params.status) query.append('status', params.status);
        if (params.semester) query.append('semester', params.semester);
        if (params.skip) query.append('skip', params.skip);
        if (params.limit) query.append('limit', params.limit);
        return this.request(`/api/students?${query.toString()}`);
    },

    getStudent(id) {
        return this.request(`/api/students/${id}`);
    },

    getStudentDetail(id) {
        return this.request(`/api/students/${id}/detail`);
    },

    createStudent(data) {
        return this.request('/api/students', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    updateStudent(id, data) {
        return this.request(`/api/students/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    deleteStudent(id) {
        return this.request(`/api/students/${id}`, {
            method: 'DELETE'
        });
    },

    async importStudentsCSV(formData) {
        const response = await fetch('/api/students/import/csv', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'CSV Import failed');
        }
        return data;
    },

    // --- Departments ---
    getDepartments() {
        return this.request('/api/departments');
    },

    createDepartment(data) {
        return this.request('/api/departments', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    updateDepartment(id, data) {
        return this.request(`/api/departments/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    deleteDepartment(id) {
        return this.request(`/api/departments/${id}`, {
            method: 'DELETE'
        });
    },

    // --- Courses ---
    getCourses(departmentId = null) {
        const query = departmentId ? `?department_id=${departmentId}` : '';
        return this.request(`/api/courses${query}`);
    },

    createCourse(data) {
        return this.request('/api/courses', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    updateCourse(id, data) {
        return this.request(`/api/courses/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    deleteCourse(id) {
        return this.request(`/api/courses/${id}`, {
            method: 'DELETE'
        });
    },

    getCourseEnrolledStudents(courseId) {
        return this.request(`/api/courses/${courseId}/enrolled-students`);
    },

    // --- Enrollments & Grades ---
    getEnrollments(params = {}) {
        const query = new URLSearchParams();
        if (params.student_id) query.append('student_id', params.student_id);
        if (params.course_id) query.append('course_id', params.course_id);
        if (params.semester_name) query.append('semester_name', params.semester_name);
        return this.request(`/api/enrollments?${query.toString()}`);
    },

    createEnrollment(data) {
        return this.request('/api/enrollments', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    updateEnrollment(id, data) {
        return this.request(`/api/enrollments/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    deleteEnrollment(id) {
        return this.request(`/api/enrollments/${id}`, {
            method: 'DELETE'
        });
    },

    // --- Attendance ---
    getAttendance(params = {}) {
        const query = new URLSearchParams();
        if (params.student_id) query.append('student_id', params.student_id);
        if (params.course_id) query.append('course_id', params.course_id);
        if (params.date) {
            query.append('date', params.date);
            query.append('date_val', params.date);
        }
        if (params.status) query.append('status', params.status);
        return this.request(`/api/attendance?${query.toString()}`);
    },

    markAttendance(data) {
        return this.request('/api/attendance', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    deleteAttendance(id) {
        return this.request(`/api/attendance/${id}`, {
            method: 'DELETE'
        });
    },

    // --- Analytics & System ---
    getStats() {
        return this.request('/api/analytics/stats');
    },

    getSystemStatus() {
        return this.request('/api/system/status');
    }
};

