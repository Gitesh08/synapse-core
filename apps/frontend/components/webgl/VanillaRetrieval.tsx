import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export function VanillaRetrieval() {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const linesRef = useRef<THREE.LineSegments>(null);
  const count = 120;
  
  const dummy = useMemo(() => new THREE.Object3D(), []);
  
  const { positions, edges } = useMemo(() => {
    const pos = [];
    const eds = [];
    for(let i = 0; i < count; i++) {
      pos.push(
        (Math.random() - 0.5) * 8,
        (Math.random() - 0.5) * 8,
        (Math.random() - 0.5) * 8
      );
    }
    // Random dense edges
    for(let i = 0; i < count; i++) {
      for(let j = i + 1; j < count; j++) {
        // High density connections
        if(Math.random() > 0.85) {
          eds.push(
            pos[i*3], pos[i*3+1], pos[i*3+2],
            pos[j*3], pos[j*3+1], pos[j*3+2]
          );
        }
      }
    }
    return { positions: new Float32Array(pos), edges: new Float32Array(eds) };
  }, [count]);

  useFrame((state) => {
    const t = state.clock.elapsedTime;
    
    // Simulate lag/search pulse
    const isSearching = (t % 4) > 2; // Lights up for 2 seconds every 4 seconds
    const pulse = isSearching ? Math.abs(Math.sin(t * 10)) : 0;
    
    if (linesRef.current) {
      const mat = linesRef.current.material as THREE.LineBasicMaterial;
      if (isSearching) {
        mat.color.setHex(0xef4444); // Red tangle
        mat.opacity = 0.5 + pulse * 0.5;
      } else {
        mat.color.setHex(0x334155); // Slate
        mat.opacity = 0.15;
      }
    }
    
    // Micro-jitters for nodes
    for (let i = 0; i < count; i++) {
      dummy.position.set(positions[i*3], positions[i*3+1], positions[i*3+2]);
      
      if (isSearching) {
        dummy.position.x += (Math.random() - 0.5) * 0.1;
        dummy.position.y += (Math.random() - 0.5) * 0.1;
      } else {
        dummy.position.x += Math.sin(t + i) * 0.05;
        dummy.position.y += Math.cos(t + i) * 0.05;
      }
      
      dummy.scale.setScalar(0.12);
      dummy.updateMatrix();
      if (meshRef.current) meshRef.current.setMatrixAt(i, dummy.matrix);
    }
    if (meshRef.current) meshRef.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      
      <instancedMesh ref={meshRef} args={[undefined, undefined, count]}>
        <sphereGeometry />
        <meshStandardMaterial color="#94A3B8" />
      </instancedMesh>
      
      <lineSegments ref={linesRef}>
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" args={[edges, 3]} />
        </bufferGeometry>
        <lineBasicMaterial transparent opacity={0.15} />
      </lineSegments>
    </>
  );
}
