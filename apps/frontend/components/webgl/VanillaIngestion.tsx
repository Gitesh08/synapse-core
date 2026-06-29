import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export function VanillaIngestion() {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const sphereRef = useRef<THREE.Mesh>(null);
  const count = 500;
  
  const dummy = useMemo(() => new THREE.Object3D(), []);
  
  // Custom particle state
  const particles = useMemo(() => {
    return Array.from({ length: count }, () => ({
      position: new THREE.Vector3(
        (Math.random() - 0.5) * 15,
        (Math.random() - 0.5) * 15,
        (Math.random() - 0.5) * 15
      ),
      velocity: new THREE.Vector3(0, 0, 0),
    }));
  }, [count]);

  useFrame((state) => {
    let hits = 0;
    
    particles.forEach((p, i) => {
      // Attract towards center
      const dir = new THREE.Vector3().copy(p.position).negate().normalize().multiplyScalar(0.02);
      p.velocity.add(dir);
      p.velocity.multiplyScalar(0.98); // Friction
      p.position.add(p.velocity);
      
      // If close to center, consider it a hit and respawn to simulate continuous ingestion
      if (p.position.length() < 1.5) {
        hits++;
        if (Math.random() > 0.8) {
          p.position.set(
            (Math.random() - 0.5) * 15,
            (Math.random() - 0.5) * 15,
            (Math.random() - 0.5) * 15
          );
          p.velocity.set(0,0,0);
        }
      }

      dummy.position.copy(p.position);
      dummy.scale.setScalar(0.08);
      dummy.updateMatrix();
      if (meshRef.current) {
        meshRef.current.setMatrixAt(i, dummy.matrix);
      }
    });
    
    if (meshRef.current) meshRef.current.instanceMatrix.needsUpdate = true;
    
    if (sphereRef.current) {
      const bloat = 1 + (hits / count) * 8 + Math.sin(state.clock.elapsedTime * 8) * 0.1;
      sphereRef.current.scale.setScalar(Math.min(bloat, 3.5));
      // Pulse red aggressively
      const intensity = 0.3 + Math.abs(Math.sin(state.clock.elapsedTime * 10)) * 0.7;
      (sphereRef.current.material as THREE.MeshStandardMaterial).emissive.setRGB(intensity, 0, 0);
    }
  });

  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      
      <instancedMesh ref={meshRef} args={[undefined, undefined, count]}>
        <boxGeometry />
        <meshStandardMaterial color="#94A3B8" />
      </instancedMesh>
      
      <mesh ref={sphereRef}>
        <sphereGeometry args={[0.5, 32, 32]} />
        <meshStandardMaterial color="#0B0F19" emissive="#ef4444" wireframe />
      </mesh>
    </>
  );
}
